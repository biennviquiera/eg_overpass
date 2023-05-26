from ProcessGameState import ProcessGameState

GAME_FILE = 'data/game_state_frame_data.parquet'
GAME = ProcessGameState(GAME_FILE)

boundary_vertices = {13: (-1735, 250), 14: (-2024, 398), 15: (-2806, 742), 16: (-2472, 1233), 17: (-1565, 580)}
minZ = 285
maxZ = 421

# b) Return whether or not each row falls within a provided boundary
print("All rows within boundary: ", GAME.all_rows_within_boundary(list(boundary_vertices.values()), minZ, maxZ))

# c) Extract the weapon classes from the inventory json column
print(GAME.get_weapon_classes())



