from ProcessGameState import ProcessGameState
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import pandas as pd


GAME_FILE = 'data/game_state_frame_data.parquet'
GAME = ProcessGameState(GAME_FILE)

boundary_vertices = {13: (-1735, 250), 14: (-2024, 398), 15: (-2806, 742), 16: (-2472, 1233), 17: (-1565, 580)}
boundary_values = list(boundary_vertices.values())
minZ = 285
maxZ = 421

# ====  1  ====
# b) Return whether or not each row falls within a provided boundary
print(f"1B: All rows within boundary: {GAME.all_rows_within_boundary(list(boundary_vertices.values()), minZ, maxZ)}")

# c) Extract the weapon classes from the inventory json column
print(f"1C: All weapon classes: {GAME.get_weapon_classes()}")


# ====  2  ====
# a) Is entering via the light blue boundary a common strategy used by
# Team2 on T (terrorist) side?
def entering_boundary_percentage(team, side):
    df = GAME.df[(GAME.df['team'] == team) & (GAME.df['side'] == side)]

    total = len(df)
    hit = 0

    for index, row in df.iterrows():
        if GAME.point_in_boundary(boundary_values, (row['x'], row['y'], row['z']), minZ, maxZ):
            hit += 1
    out = hit/total
    return out

team_2_t_side_boundary = entering_boundary_percentage("Team2", "T")
print(f"2A: Entering via the boundary a common strategy used by Team2 on T side: {team_2_t_side_boundary}") 

# b) What is the average timer that Team2 on T (terrorist) side enters
# “BombsiteB” with least 2 rifles or SMGs?
def average_timer_enter_area(team, side, area):
    df = GAME.df[(GAME.df['team'] == team) & (GAME.df['side'] == side)].copy()

    df.loc[:, 'rifles_or_SMGs'] = df['inventory'].apply(
        lambda inventory: sum(1 for item in inventory if item['weapon_class'].lower() in ['rifle', 'smg']) if inventory is not None else 0
    )

    df = df.groupby(['round_num']).agg({'rifles_or_SMGs': 'sum'}).reset_index()

    rounds_with_2_or_more_weapons = df[df['rifles_or_SMGs'] >= 2]['round_num']

    df = GAME.df[(GAME.df['team'] == 'Team2') & (GAME.df['side'] == 'T') & (GAME.df['round_num'].isin(rounds_with_2_or_more_weapons))]
    df_area = df[df['area_name'] == area]

    df_area.loc[:, 'clock_time'] = df_area['clock_time'].apply(
        lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1])
    )

    average_time = df_area['clock_time'].mean()

    average_minutes = int(average_time // 60)
    average_seconds = int(average_time % 60)
    return f"{average_minutes}:{average_seconds:02d}"
output = average_timer_enter_area("Team2", "T", "BombsiteB")
print(f"2B: Average time that Team2 on T side enters BombsiteB with at least 2 rifles or SMGs: {output}")


# c. Now that we’ve gathered data on Team2 T side, let's examine their CT
# (counter-terrorist) Side. Using the same data set, tell our coaching
# staff where you suspect them to be waiting inside “BombsiteB”

def area_heatmap(df, team, side, area):
    """
    Creates a heatmap of locations in team playing on a given side in an area
    """
    plt.figure(figsize=(10,8))
    df_limited = df[(df['team'] == team) & (df['side'] == side) & (df['area_name'] == area)]

    global_x_min = df['x'].min()
    global_x_max = df['x'].max()
    global_y_min = df['y'].min()
    global_y_max = df['y'].max()

    heatmap, xedges, yedges = np.histogram2d(df_limited['x'], df_limited['y'], bins=(100,100), range=[[global_x_min, global_x_max], [global_y_min, global_y_max]])
    extent = [global_x_min, global_x_max, global_y_min, global_y_max]

    adjustment_right = 500
    adjustment_left = -800
    adjustment_up = 200
    adjustment_down = -200
    img_extent = [global_x_min + adjustment_left, global_x_max + adjustment_right, global_y_min + adjustment_down, global_y_max + adjustment_up]


    plt.imshow(heatmap.T, origin='lower', extent=extent, cmap='YlOrRd')
    plt.colorbar(label='Number of points')
    # overlay image
    img = mpimg.imread('map/de_overpass_radar.jpeg')  # replace with your image file
    plt.imshow(img, extent=img_extent, alpha=0.2)  # adjust alpha to change overlay transparency

    plt.title(f'de_overpass Position Heatmap: {team} On {side} At {area}')
    plt.show()

area_heatmap(GAME.df.copy(), 'Team1', 'T', 'BombsiteB')
area_heatmap(GAME.df.copy(), 'Team1', 'T', 'BombsiteA')


def map_heatmap_bomb(df, team, side, bomb_status):
    """
    Creates a heatmap of locations belong to team on some side when the bomb has been planted
    """
    plt.figure(figsize=(10,8))
    df_limited = df[(df['team'] == team) & (df['side'] == side) & (df['bomb_planted'] == bomb_status)]

    global_x_min = df['x'].min()
    global_x_max = df['x'].max()
    global_y_min = df['y'].min()
    global_y_max = df['y'].max()

    heatmap, xedges, yedges = np.histogram2d(df_limited['x'], df_limited['y'], bins=(100,100), range=[[global_x_min, global_x_max], [global_y_min, global_y_max]])
    extent = [global_x_min, global_x_max, global_y_min, global_y_max]

    adjustment_right = 500
    adjustment_left = -800
    adjustment_up = 200
    adjustment_down = -200
    img_extent = [global_x_min + adjustment_left, global_x_max + adjustment_right, global_y_min + adjustment_down, global_y_max + adjustment_up]

    img = mpimg.imread('map/de_overpass_radar.jpeg')

    plt.imshow(heatmap.T, origin='lower', extent=extent, cmap='YlOrRd')
    plt.colorbar(label='Number of points')
    # overlay image
    plt.imshow(img, extent=img_extent, alpha=0.2)

    plt.title(f'de_overpass Position Heatmap: {team} On {side} When Bomb %s Planted' %("Is" if bomb_status is True else "Is Not"))
    plt.show()

map_heatmap_bomb(GAME.df.copy(), 'Team1', 'T', False)
map_heatmap_bomb(GAME.df.copy(), 'Team1', 'T', True)
