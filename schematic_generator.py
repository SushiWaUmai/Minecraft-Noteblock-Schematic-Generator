import os
import sys
from litemapy import Schematic, Region, BlockState
from AudioSplitter import split_midi


air = BlockState('minecraft:air')
repeater = BlockState('minecraft:repeater')
ticked_repeater = BlockState('minecraft:repeater', { 'delay' : '4' })
white_concrete = BlockState('minecraft:white_concrete')
redstone = BlockState('minecraft:redstone_wire')
observer_down = BlockState('minecraft:observer', { 'facing' : 'down' })
powered_rail = BlockState('minecraft:powered_rail', {'shape' : 'east_west' })
redstone_block = BlockState('minecraft:redstone_block')
redstone_lamp = BlockState('minecraft:redstone_lamp')
sticky_piston = BlockState('minecraft:sticky_piston', { 'facing' : 'south' })
lever = BlockState('minecraft:lever', { 'face' : 'floor' })

instrument_blocks = (
	BlockState('minecraft:oak_planks'),
	BlockState('minecraft:white_wool'),
	BlockState('minecraft:dirt'),
	BlockState('minecraft:clay'),
	BlockState('minecraft:gold_block')
)

def create_platforms(reg):
	for x in reg.xrange():
		for z in reg.zrange():
			reg.setblock(x, 0, z, white_concrete)
			reg.setblock(x, 6, z, white_concrete)


def create_repeater(reg, width, start=0):
	first = (start + 5) % 2
	for z in reg.zrange():
		if z >= 5:
			if z % 2 == first:
				reg.setblock(width+1, 1, z, repeater)
				reg.setblock(width-1, 1, z, repeater)
			else:
				reg.setblock(width+1, 1, z, redstone_lamp)
				reg.setblock(width-1, 1, z, redstone_lamp)



def create_firstlayer(reg, width, start=0):
	first = (start + 5) % 2
	for z in reg.zrange():
		if z >= start + 5:
			if z % 2 != first:
				reg.setblock(width+1, 2, z, observer_down)
			else:
				reg.setblock(width-1, 2, z, observer_down)


def create_toplayer(reg, start=0):
	for z in reg.zrange():
		if z < start + 5:
			continue
		for x in reg.xrange():
			reg.setblock(x, 3, z, white_concrete)
			reg.setblock(x, 4, z, powered_rail)
			reg.setblock(x, 5, z, observer_down)


def create_redstonelamps(reg, width, start=0):
	for z in reg.zrange():
		if z >= start + 5:
			reg.setblock(width, 7, z, redstone_lamp)			


def create_layers(reg, width, start=0):
	create_platforms(reg)
	create_repeater(reg, width, start)
	create_firstlayer(reg, width, start)
	create_toplayer(reg, start)
	create_redstonelamps(reg, width, start)

def create_start(reg, width, start=0):
	reg.setblock(width, 7, start, lever)

	create_staircase(reg, width, start)
	create_nonpiston_connection(reg, width, start)
	create_piston_connection(reg, width, start)


def create_staircase(reg, width, start=0):
	# first block
	reg.setblock(width  , 5, start+0, redstone)
	reg.setblock(width  , 4, start+0, white_concrete)

	# second block
	reg.setblock(width  , 4, start+1, redstone)
	reg.setblock(width  , 3, start+1, white_concrete)

	# third block
	reg.setblock(width+1, 3, start+1, redstone)
	reg.setblock(width+1, 2, start+1, white_concrete)

	# forth block
	reg.setblock(width+1, 2, start+0, redstone)
	reg.setblock(width+1, 1, start+0, white_concrete)


def create_nonpiston_connection(reg, width, start=0):
	# One game tick repeater
	reg.setblock(width+1, 1, start+1, repeater)

	# Connection to noteblock repeaters
	reg.setblock(width+1, 1, start+2, redstone)
	reg.setblock(width+1, 1, start+3, redstone)
	reg.setblock(width+1, 1, start+4, redstone)


def create_piston_connection(reg, width, start=0):
	# Connection to the right side
	reg.setblock(width  , 1, start+0, redstone)
	reg.setblock(width-1, 1, start+0, redstone)
	reg.setblock(width-2, 1, start+0, redstone)

	# Connection to Piston with block
	reg.setblock(width-2, 1, start+1, white_concrete)
	reg.setblock(width-2, 2, start+1, redstone)

	# Piston and block
	reg.setblock(width-2, 2, start+2, sticky_piston)
	reg.setblock(width-2, 2, start+3, white_concrete)

	# Redstone block and redstone wire under piston block
	reg.setblock(width-2, 1, start+3, redstone)
	reg.setblock(width-2, 0, start+3, redstone_block)

	# Connection to noteblock repeaters
	reg.setblock(width-1, 1, start+3, white_concrete)
	reg.setblock(width-1, 2, start+3, redstone)
	reg.setblock(width-1, 1, start+4, redstone)


def time_to_coord(time):
	return round(time * 20)


def create_note_block(reg, width, note, instrument_block, start):
	# print(note.velocity)
	vel_pos = 7 - round((note.velocity * 7) / 128)
	coord = time_to_coord(note.start) + start + 5
	props = { 'note' : str(note.pitch - 54) }
	note_block = BlockState('minecraft:note_block', props)

	if vel_pos > 7 / 2:
		vel_add = -1
	else:
		vel_add = 1

	while True:
		if reg.getblock(width + vel_pos, 7, coord) == air:
			reg.setblock(width + vel_pos, 7, coord, note_block)
			reg.setblock(width + vel_pos, 6, coord, instrument_block)
			break
		elif reg.getblock(width - vel_pos, 7, coord) == air:
			reg.setblock(width - vel_pos, 7, coord, note_block)
			reg.setblock(width - vel_pos, 6, coord, instrument_block)
			break
		vel_pos += vel_add


def create_note_blocks(reg, width, audio_file, start=0):
	for i, instrument in enumerate(audio_file.instruments):
		for note in instrument.notes:
			create_note_block(reg, width, note, instrument_blocks[i], start)


def generate_schematic(file_path, save_path=None, width=7, start=5, author='Minecraft-Noteblock-Schematic-Generator', description=''):
	audio_file = split_midi(file_path)

	reg = Region(0, 0, 0, width*2+1, 8, time_to_coord(audio_file.get_end_time()))
	
	create_layers(reg, width, start)
	create_start(reg, width, start)
	create_note_blocks(reg, width, audio_file, start)

	basename = os.path.splitext(os.path.basename(file_path))[0]
	if save_path is None:
		appdata_dir = os.environ.get('appdata')
		save_path = os.path.join(appdata_dir, '.minecraft', 'schematics', f'{basename}.litematic')
	
	schem = reg.as_schematic(name=basename, author=author, description=description)
	schem.save(save_path)

if __name__ == '__main__':
	generate_schematic(sys.argv[1])
