from pyrsistent import m

'''Ocean Optics Spectrometer Configurations'''

# end points
end_points = m(
    EP1_OUT=0x01,
    EP1_IN=0x81,
    EP2_OUT=0x02,
    EP2_IN=0x82,
    EP6_OUT=0x06,
    EP6_IN=0x86,
    EP7_OUT=0x07,
    EP7_IN=0x87
)

# Ocean Optics USB Vendor ID
vendor_ids = m(
    OCEANOPTICS_VENDOR=0x2457
)

# Spectrometer command set
command_set = m(
    SPECTR_INIT=0x01,
    SPECTR_SET_INTEGRATION_TIME=0x02,
    SPECTR_QUERY_INFORMATION=0x05,
    SPECTR_REQUEST_SPECTRA=0x09,
    SPECTR_WRITE_REG_INFO=0x6A,
    SPECTR_READ_PCB_TEMP=0x6C,
    SPECTR_QUERY_STATUS=0xFE
)

# Ocean Optics spectrometers list
# (device id, 'model name', packet size, cmd end point out, data end point in, size, spectra end point in, size)
model_configs = (
    ([0x102A], 'Maya2000 Pro', 4609, end_points['EP1_OUT'], end_points['EP1_IN'], 64, end_points['EP2_IN'], 512),
    ([0x1026, 0x1028], 'NIRQUEST', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 512, end_points['EP2_IN'], 512),
    ([0x101E], 'USB2000+', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 64, end_points['EP2_IN'], 512),
    ([0x1016, 0x1012], 'HR2000+', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 64, end_points['EP2_IN'], 512),
    ([0x4004], 'QE65 Pro', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 64, end_points['EP2_IN'], 512),
    ([0x1018], 'QE65000', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 64, end_points['EP2_IN'], 512),
    ([0x1002], 'USB2000', 4097, end_points['EP2_OUT'], end_points['EP7_IN'], 64, end_points['EP2_IN'], 64),
    ([0x1014], 'USB650', 4097, end_points['EP2_OUT'], end_points['EP7_IN'], 64, end_points['EP2_IN'], 64),
    ([0x100A, 0x1009], 'HR2000', 4097, end_points['EP2_OUT'], end_points['EP7_IN'], 64, end_points['EP2_IN'], 64),
    ([0x1040], 'Torus', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 64, end_points['EP2_IN'], 512),
    ([0x1044], 'Apex', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 64, end_points['EP2_IN'], 512),
    ([0x102C], 'Maya', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 64, end_points['EP2_IN'], 512),
    ([0x2000], 'Jaz', 4097, end_points['EP1_OUT'], end_points['EP1_IN'], 512, end_points['EP2_IN'], 512),
    ([0x1010, 0x100C], 'NIR', 4097, end_points['EP2_OUT'], end_points['EP7_IN'], 64, end_points['EP7_IN'], 64)
)
