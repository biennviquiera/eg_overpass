import pandas as pd

class ProcessGameState:
    def __init__(self, data):
        self.df = pd.read_parquet(data)

    #raycasting algorithm to check if the point is within the boundary
    def point_in_boundary(self, boundary, point, minZ, maxZ):
        x, y, z = point
        n = len(boundary)
        if z < minZ or z > maxZ:
            return False
        inside = False

        p1x, p1y = boundary[0]


        for i in range(n + 1):
            p2x, p2y = boundary[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            x_intersection = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= x_intersection:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside
    
    def all_rows_within_boundary(self, boundary, minZ, maxZ) -> bool:
        """
        Returns a boolean whether or not all of the rows in the currently loaded game is within the boundary
        """
        
        for index, row in self.df.iterrows():
            if not self.point_in_boundary(boundary, (row['x'], row['y'], row['z']), minZ, maxZ) : return False
        return True
    
    def get_weapon_classes(self):
        """
        Extracts the weapon classes from the inventory json column
        """
        weapon_classes = set()
        for index, row in self.df.iterrows():
            inv = row['inventory']
            if inv is not None:
                for item in inv:
                    weapon_classes.add(item['weapon_class'])
        return weapon_classes