from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

duck = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'TL074', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TL074'}), 'ref_prefix':'U', 'fplist':['', ''], 'footprint':'Package_DIP:DIP-14_W7.62mm', 'keywords':'quad opamp', 'description':'Quad Low-Noise JFET-Input Operational Amplifiers, DIP-14/SOIC-14', 'datasheet':'http://www.ti.com/lit/ds/symlink/tl071.pdf', 'pins':[
            Pin(num='1',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='+',func=pin_types.INPUT,unit=2),
            Pin(num='6',name='-',func=pin_types.INPUT,unit=2),
            Pin(num='7',func=pin_types.OUTPUT,unit=2),
            Pin(num='8',func=pin_types.OUTPUT,unit=3),
            Pin(num='9',name='-',func=pin_types.INPUT,unit=3),
            Pin(num='10',name='+',func=pin_types.INPUT,unit=3),
            Pin(num='12',name='+',func=pin_types.INPUT,unit=4),
            Pin(num='13',name='-',func=pin_types.INPUT,unit=4),
            Pin(num='14',func=pin_types.OUTPUT,unit=4),
            Pin(num='4',name='V+',func=pin_types.PWRIN,unit=5),
            Pin(num='11',name='V-',func=pin_types.PWRIN,unit=5)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '3', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '7', '6']},{'label': 'uC', 'num': 3, 'pin_nums': ['8', '10', '9']},{'label': 'uD', 'num': 4, 'pin_nums': ['14', '13', '12']},{'label': 'uE', 'num': 5, 'pin_nums': ['11', '4']}] }),
        Part(**{ 'name':'Barrel_Jack', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Barrel_Jack'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_BarrelJack:BarrelJack_Horizontal', 'keywords':'DC power barrel jack connector', 'description':'DC Barrel Jack', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'1N5817', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'1N5817'}), 'ref_prefix':'D', 'fplist':['Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal', 'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal'], 'footprint':'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal', 'keywords':'diode Schottky', 'description':'20V 1A Schottky Barrier Rectifier Diode, DO-41', 'datasheet':'http://www.vishay.com/docs/88525/1n5817.pdf', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'C_Polarized', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C_Polarized'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_THT:CP_Radial_D5.0mm_P2.50mm', 'keywords':'cap capacitor', 'description':'Polarized capacitor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'R', 'fplist':[''], 'footprint':'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical', 'keywords':'R res resistor', 'description':'Resistor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AudioJack2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AudioJack2'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_Audio:Jack_6.35mm_Neutrik_NJ3FD-V_Vertical', 'keywords':'audio jack receptacle mono phone headphone TS connector', 'description':'Audio Jack, 2 Poles (Mono / TS)', 'datasheet':'', 'pins':[
            Pin(num='S',func=pin_types.PASSIVE,unit=1),
            Pin(num='T',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_THT:C_Rect_L7.0mm_W2.5mm_P5.00mm', 'keywords':'cap capacitor', 'description':'Unpolarized capacitor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'R_Potentiometer', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R_Potentiometer'}), 'ref_prefix':'RV', 'fplist':[''], 'footprint':'Potentiometer_THT:Potentiometer_Alps_RK097_Single_Horizontal', 'keywords':'resistor variable', 'description':'Potentiometer', 'datasheet':'', 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='3',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'1N4148', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'1N4148'}), 'ref_prefix':'D', 'fplist':['Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal', 'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal'], 'footprint':'Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_AnodeUp', 'keywords':'diode', 'description':'100V 0.15A standard switching diode, DO-35', 'datasheet':'https://assets.nexperia.com/documents/data-sheet/1N4148_1N4448.pdf', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'R_Potentiometer_Dual_Separate', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R_Potentiometer_Dual_Separate'}), 'ref_prefix':'RV', 'fplist':[''], 'footprint':'Potentiometer_THT:Potentiometer_Alps_RK097_Dual_Horizontal', 'keywords':'resistor variable', 'description':'Dual potentiometer, separate units', 'datasheet':'', 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='4',func=pin_types.PASSIVE,unit=2),
            Pin(num='5',name='5',func=pin_types.PASSIVE,unit=2),
            Pin(num='6',name='6',func=pin_types.PASSIVE,unit=2)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '3']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '4', '6']}] }),
        Part(**{ 'name':'LM13700', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM13700'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'Package_DIP:DIP-16_W7.62mm', 'keywords':'operational transconductance amplifier OTA', 'description':'Dual Operational Transconductance Amplifiers with Linearizing Diodes and Buffers, DIP-16/SOIC-16', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm13700.pdf', 'pins':[
            Pin(num='12',func=pin_types.OUTPUT,unit=1),
            Pin(num='13',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='14',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='15',name='DIODE_BIAS',func=pin_types.INPUT,unit=1),
            Pin(num='16',func=pin_types.INPUT,unit=1),
            Pin(num='9',func=pin_types.OUTPUT,unit=2),
            Pin(num='10',func=pin_types.INPUT,unit=2),
            Pin(num='1',func=pin_types.INPUT,unit=3),
            Pin(num='2',name='DIODE_BIAS',func=pin_types.INPUT,unit=3),
            Pin(num='3',name='+',func=pin_types.INPUT,unit=3),
            Pin(num='4',name='-',func=pin_types.INPUT,unit=3),
            Pin(num='5',func=pin_types.OUTPUT,unit=3),
            Pin(num='7',func=pin_types.INPUT,unit=4),
            Pin(num='8',func=pin_types.OUTPUT,unit=4),
            Pin(num='6',name='V-',func=pin_types.PWRIN,unit=5),
            Pin(num='11',name='V+',func=pin_types.PWRIN,unit=5)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['12', '15', '13', '16', '14']},{'label': 'uB', 'num': 2, 'pin_nums': ['10', '9']},{'label': 'uC', 'num': 3, 'pin_nums': ['1', '4', '2', '5', '3']},{'label': 'uD', 'num': 4, 'pin_nums': ['7', '8']},{'label': 'uE', 'num': 5, 'pin_nums': ['11', '6']}] })])