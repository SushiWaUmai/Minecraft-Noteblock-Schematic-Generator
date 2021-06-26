from litemapy import Schematic, Region, BlockState
from AudioSplitter import split_midi
import sys
import os
from tqdm import tqdm
from tqdm.contrib import tenumerate

air_state = BlockState('minecraft:air')
redstone_repeater = BlockState('minecraft:repeater')
white_concrete = BlockState('minecraft:white_concrete')
redstone = BlockState('minecraft:redstone_wire')
observer_west = BlockState('minecraft:observer', { 'facing' : 'west' })
observer_down = BlockState('minecraft:observer', { 'facing' : 'down' })
powered_rail = BlockState('minecraft:powered_rail', {'shape' : 'east_west' })

instrument_blocks = (
	BlockState('minecraft:oak_planks'),
	BlockState('minecraft:white_wool'),
	BlockState('minecraft:white_concrete'),
	BlockState('minecraft:clay'),
	BlockState('minecraft:gold_block')
)

appdata_dir = os.environ.get('appdata')


def time_to_coord(time):
	return round(time * 20)

def add_note_block(reg, coord, block, instrument):
	i = 1
	while True:
		if reg.getblock(i, 4, coord) == air_state:
			reg.setblock(i, 4, coord, block)
			reg.setblock(i, 3, coord, instrument)
			break
		i += 1

def fill_redstone(reg):
	for x, y, z in reg.allblockpos():
		if reg.getblock(x, y, z) == air_state:
			if y == 0:
				reg.setblock(x, y, z, white_concrete)
			elif y == 1:
				if x == 0:
					reg.setblock(x, y, z, observer_west)
				else:
					reg.setblock(x, y, z, powered_rail)
			elif y == 2:
				if x != 0:
					reg.setblock(x, y, z, observer_down)
			elif y == 3:
				if x != 0:
					reg.setblock(x, y, z, white_concrete)

def generate_schematic(file_path, save_path=None):
	basename = os.path.splitext(os.path.basename(file_path))[0]
	print(f"Chosen mid file: {file_path}")


	audio_file = split_midi(file_path)
	
	print('Creating Region...')
	reg = Region(0, 0, 0, 10, 5, time_to_coord(audio_file.get_end_time() + 1))
	schem = reg.as_schematic(name=basename, author='SushiWaUmai', description='')

	print('Adding Note Blocks...')
	for i, instrument in tenumerate(audio_file.instruments):
		for note in instrument.notes:
			props = {
				'note' : str(note.pitch - 54)
			}
			note_block = BlockState('minecraft:note_block', props)
			add_note_block(reg, time_to_coord(note.start + 1), note_block, instrument_blocks[i])
	
	print('Adding other stuff...')
	fill_redstone(reg)

	if save_path is None:
		save_path = os.path.join(appdata_dir, '.minecraft', 'schematics', '{basename}.litematic')
	schem.save(save_path)
	print(f"Schematic file saved in under {save_path}")


if __name__ == '__main__':
	generate_schematic(sys.argv[1])