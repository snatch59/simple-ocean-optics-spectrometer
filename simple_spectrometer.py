import usb.core
import usb.util
import struct
import matplotlib.pyplot as plt
import ocean_optics_configs as config


def find_spectrometer():
    _usb_device = None
    _device_id = None
    _model_name = 'unknown'
    _packet_size = 0
    _commands_ep_out = 0
    _data_ep_in = 0
    _data_ep_in_size = 0
    _spectra_ep_in = 0
    _spectra_ep_in_size = 0

    # find any vendor devices
    usb_devices = usb.core.find(find_all=True, idVendor=config.vendor_ids['OCEANOPTICS_VENDOR'])

    # was it found?
    if usb_devices is None:
        raise ValueError('No Vendor Spectrometers found')

    # We've found one or more spectrometers
    for _usb_device in usb_devices:
        print('Product Id: ' + hex(_usb_device.idProduct))

        # find device id in product_ids (we only use the first spectrometer found
        spectrometer = [item for item in config.product_configs if item[0][0] == _usb_device.idProduct]
        if spectrometer:
            # load in its configuration
            _device_id = spectrometer[0][0][0]
            _model_name = spectrometer[0][1]
            _packet_size = spectrometer[0][2]
            _commands_ep_out = spectrometer[0][3]
            _data_ep_in = spectrometer[0][4]
            _data_ep_in_size = spectrometer[0][5]
            _spectra_ep_in = spectrometer[0][6]
            _spectra_ep_in_size = spectrometer[0][7]
            print(_model_name, 'found ...')

            # use and set USB configuration for first spectrometer found
            _usb_device.set_configuration()

    return _usb_device, _device_id, _model_name, _packet_size, _commands_ep_out, \
        _data_ep_in, _data_ep_in_size, _spectra_ep_in, _spectra_ep_in_size


def drop_spectrometer(usb_device):
    usb.util.dispose_resources(usb_device)


def write_register(usb_device, the_register, reg_value, epo=None):
    if epo is None:
        epo = config.end_points['EP1_OUT']

    # little endian, unsigned char, unsigned int
    usb_send(usb_device, epo, struct.pack(
        '<BBH', config.command_set['SPECTR_WRITE_REG_INFO'],
        the_register, int(reg_value)))


def usb_send(usb_device, data, epo=None):
    if epo is None:
        epo = config.end_points['EP1_OUT']

    usb_device.write(epo, data)


def usb_read(usb_device, epi=None, epi_size=None):
    if epi is None:
        epi = config.end_points['EP2_IN']
    if epi_size is None:
        epi_size = 512

    return usb_device.read(epi, epi_size)


def usb_query(usb_device, data, epo=None, epi=None, epi_size=None):
    usb_send(usb_device, data, epo)
    return usb_read(usb_device, epi, epi_size)


def query_information(usb_device, commands_epo, data_epi, address, raw=False):
    # little endian, unsigned char, unsigned char
    ret = usb_query(usb_device,
                    struct.pack('<BB', config.command_set['SPECTR_QUERY_INFORMATION'], int(address)),
                    epo=commands_epo, epi=data_epi, epi_size=17)
    if bool(raw):
        return ret
    if ret[0] != config.command_set['SPECTR_QUERY_INFORMATION'] or ret[1] != int(address) % 0xFF:
        raise ValueError('query_information: Wrong answer')

    return ret[2:ret[2:].index(0)+2].tostring()


def query_status(usb_device, commands_epo, data_epi):
    # little endian, unsigned char, unsigned char
    ret = usb_query(usb_device, struct.pack('<B', config.command_set['SPECTR_QUERY_STATUS']),
                    epo=commands_epo, epi=data_epi, epi_size=17)

    # little endian, unsigned short, unsigned long, unsigned char x 10
    statusdata = struct.unpack('<HLBBBBBBBBBB', ret[:])
    status = {'pixels': statusdata[0],
              'integration_time': statusdata[1],
              'lamp_enable': statusdata[2],
              'trigger_mode': statusdata[3],
              'acquisition_status': statusdata[4],
              'packets_in_spectrum': statusdata[5],
              'power_down': statusdata[6],
              'packets_in_endpoint': statusdata[7],
              'usb_speed': statusdata[10]
              }

    return status


def request_spectrum(usb_device, packet_size, spectra_epi, commands_epo):
    usb_send(usb_device, struct.pack('<B', config.command_set['SPECTR_REQUEST_SPECTRA']), epo=commands_epo)

    data = usb_read(usb_device, epi=spectra_epi, epi_size=packet_size)
    if len(data) == packet_size and data[packet_size - 1] == 0x69:
        spectrum = []
        for i in range(0, 4096, 2):
            databytes = [data[i], data[i + 1]]
            intval = int.from_bytes(databytes, byteorder='little')
            spectrum.append(intval)
        spectrum[1] = spectrum[0]
        return spectrum
    else:
        return 0


def spectrometer_init(usb_device, commands_epo):
    # little endian, unsigned char
    usb_send(usb_device, struct.pack('<B', config.command_set['SPECTR_INIT']), epo=commands_epo)


def set_integration_time(usb_device, time_us, spec_commands_to):
    # little endian, unsigned char, unsigned int
    usb_send(usb_device, struct.pack('<BI', config.command_set['SPECTR_SET_INTEGRATION_TIME'], int(time_us)),
             epo=spec_commands_to)


def get_integration_time(usb_device, spec_commands_to, spec_data_from):
    integ_time = query_status(usb_device, spec_commands_to, spec_data_from)['integration_time']
    print('Integration Time (us): ', integ_time)


def get_spectrometer_info(usb_device, spec_commands_to, spec_data_from):
    bindata = query_information(usb_device, spec_commands_to, spec_data_from, 0)
    serial_number = bindata.decode("utf-8")
    print('Serial Number: ', serial_number)

    wl_factors = [float(query_information(usb_device, spec_commands_to, spec_data_from, i)) for i in range(1, 5)]
    print("Wavelength Calibration Coefficients:")
    print(*wl_factors, sep="\n")

    stray_light_constant = float(query_information(usb_device, spec_commands_to, spec_data_from, 5))
    print('Stray Light Const: ', stray_light_constant)

    nl_factors = [float(query_information(usb_device, spec_commands_to, spec_data_from, i)) for i in range(6, 14)]
    print("Non-Linearity Correlation Coefficients: ")
    print(*nl_factors, sep="\n")

    polynomial_order_nonlincal = int(query_information(usb_device, spec_commands_to, spec_data_from, 14))
    print("Polynomial Order for Non-Linearity Correlation Coefficients:", polynomial_order_nonlincal)

    bindata = query_information(usb_device, spec_commands_to, spec_data_from, 15)
    grating_info = bindata.decode("utf-8")
    grating_params = grating_info.split()
    print("Grating ID: ", grating_params[0])
    print("Filter Wavelength: ", grating_params[1])
    print("Slit Size ", grating_params[2])

    bindata = query_information(usb_device, spec_commands_to, spec_data_from, 16)
    spectrometer_info = bindata.decode("utf-8")
    array_coating_manufacturer = spectrometer_info[0]
    array_range = spectrometer_info[1]
    l2_lens_installed = spectrometer_info[2]
    cpld_version = spectrometer_info[4]
    print("Array Coating Manufacturer: ", array_coating_manufacturer)
    print("Array Range: ", array_range)
    print("L2 Lens Installed: ", l2_lens_installed)
    print("CPLD Version: ", cpld_version)


if __name__ == '__main__':
    usbDevice, spectrometer_id, model_name, spectra_packet_size, cmds_ep_out, data_ep_in, data_ep_in_size, \
        spectra_ep_in, spectra_ep_in_size = find_spectrometer()

    if usbDevice is None:
        print('No Ocean Optics Devices Found')
    elif spectrometer_id is None:
        print('No Known Ocean Optics Spectrometer Found')
    else:
        spectrometer_init(usbDevice, cmds_ep_out)
        get_spectrometer_info(usbDevice, cmds_ep_out, data_ep_in)
        set_integration_time(usbDevice, 1000000, cmds_ep_out)           # integration time in micro-seconds
        get_integration_time(usbDevice, cmds_ep_out, data_ep_in)

        # plot the acquired spectrum
        plt.ion()
        try:
            while True:
                acquired = request_spectrum(usbDevice, spectra_packet_size, spectra_ep_in, cmds_ep_out)
                plt.title(model_name)
                plt.plot(acquired)
                plt.pause(0.5)
                plt.cla()
        except KeyboardInterrupt:
            # Exit on CTRL-C
            pass

        print("exiting and cleaning up USB comms ...")
        drop_spectrometer(usbDevice)
