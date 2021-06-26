from litemapy import Schematic, Region, BlockState

props = {
	'note': '10'
}

reg = Region(0, 0, 0, 21, 21, 21)
schem = reg.as_schematic(name='Hello World', author='SushiWaUmai', description='This is a Hello World Test')

note_block = BlockState('minecraft:note_block', props)

print("Block Stuff")
print(dir(note_block))
print("Properties Stuff")
print(dir(note_block._BlockState__properties))
print("Validate Stuff")
print(note_block._BlockState__validate('note', '10'))

print(note_block._BlockState__properties)

for x, y, z in reg.allblockpos():
	if round(((x-10)**2 + (y - 10)**2 + (z - 10)**2)**0.5) <= 10:
		reg.setblock(x, y, z, note_block)

schem.save('Hello_World.litematic')