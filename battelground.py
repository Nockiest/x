import random
import pygame
 
def do_lines_intersect(p1, p2, p3, p4):
    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    o1 = orientation(p1, p2, p3)
    o2 = orientation(p1, p2, p4)
    o3 = orientation(p3, p4, p1)
    o4 = orientation(p3, p4, p2)

    if o1 != o2 and o3 != o4:
        if min(p1[0], p2[0]) <= max(p3[0], p4[0]) and min(p3[0], p4[0]) <= max(p1[0], p2[0]) and \
           min(p1[1], p2[1]) <= max(p3[1], p4[1]) and min(p3[1], p4[1]) <= max(p1[1], p2[1]):
            # Calculate the point of intersection
            intersect_x = (o1 * p3[0] - o2 * p4[0]) / (o1 - o2)
            intersect_y = (o1 * p3[1] - o2 * p4[1]) / (o1 - o2)
            return intersect_x, intersect_y

    return False
class BattleGround:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.forrests = []
        self.rivers = []# [(0, 0), (400, 300)]#[(0,0),(100, 200),(300,300), (350, 200)]
        self.towns = []
        self.roads = []
        self.supply_depots = []
        
        # Define quantities of each element to generate
        self.num_forrests = 10
        self.num_rivers = 3
        self.num_towns = 4
        self.num_roads = 9
        self.num_supply_depots = 2

    def place_forrests(self):
        for _ in range(self.num_forrests):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.forrests.append((x, y))

    def place_rivers(self):
        for _ in range(self.num_rivers):
            start_x = random.choice([0, self.width])
            start_y = random.randint(0, self.height)
            end_x = self.width - start_x
            end_y = random.randint(0, self.height)

            control_x1 = random.randint(0, self.width)
            control_y1 = random.randint(0, self.height)
            control_x2 = random.randint(0, self.width)
            control_y2 = random.randint(0, self.height)

            points = []
            num_segments = 10
            intersection_point = None  # Initialize the intersection point as None

            for i in range(num_segments + 1):
                t = i / num_segments
                point = self.calculate_bezier_curve(t, (start_x, start_y), (control_x1, control_y1), (control_x2, control_y2), (end_x, end_y))
                rounded_point = (round(point[0]), round(point[1]))
                intersects = False  # Initialize the intersection flag as False
                points.append(rounded_point)

                for existing in self.rivers:
                    for j in range(len(existing) - 1):
                        intersection = do_lines_intersect(points[len(points) - 2], rounded_point, existing[j], existing[j+1])
                        if intersection:
                            intersects = True  # Set the intersection flag to True
                            intersection_point = existing[j+1]  # Store the intersection point
                            break  # Break the inner loop once an intersection is found

                    if intersects:  # If an intersection is found, break the outer loop
                        break

                if intersects:  # If an intersection is found, break the loop and do not add the river
                    break

            if intersection_point:
                points[-1] = intersection_point  # Replace the last point with the intersection point

            # Only add the river if there were no intersections
            self.rivers.append(points)


                    # if intersects:  # If an intersection is found, stop generating the river
                    #     break

                    #         # print(points, self.rivers)
                    #         self.rivers.append(points)  # Add the river if there was no intersection
                    #         break
                    #  print(rounded_point,river,"y" )
                 # Check for intersections with other rivers
                
                 # if any(check_intersection(rounded_point, existing_river) for existing_river in self.rivers):
                 #     break

             
    

    
    def calculate_bezier_curve(self, t, p0, p1, p2, p3):
        u = 1 - t
        uu = u * u
        uuu = uu * u
        tt = t * t
        ttt = tt * t

        p = (
            u * uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0],
            u * uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
        )
        return p

    def place_towns(self):
        for _ in range(self.num_towns):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.towns.append((x, y))

    def place_roads(self):
        for _ in range(self.num_roads):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            self.roads.append(((x1, y1), (x2, y2)))

    def place_supply_depots(self):
    # Place supply depots on the left side
        for _ in range(self.num_supply_depots // 2):
            x_left = random.randint(50, self.width // 2 - 50)  # Ensure at least 50 pixels from the left edge
            y = random.randint(50, self.height - 50)  # Ensure at least 50 pixels from top and bottom edges
            self.supply_depots.append((x_left, y))

        # Place supply depots on the right side
        for _ in range(self.num_supply_depots // 2):
            x_right = random.randint(self.width // 2 + 50, self.width - 50)  # Ensure at least 50 pixels from the right edge
            y = random.randint(50, self.height - 50)  # Ensure at least 50 pixels from top and bottom edges
            self.supply_depots.append((x_right, y))

    def draw_bezier_curve(self, screen, points):
            num_segments = 100
            curve_points = []
            for t in range(num_segments + 1):
                t_normalized = t / num_segments
                x = int((1 - t_normalized)**3 * points[0][0] +
                        3 * (1 - t_normalized)**2 * t_normalized * points[2][0] +
                        3 * (1 - t_normalized) * t_normalized**2 * points[3][0] +
                        t_normalized**3 * points[1][0])
                y = int((1 - t_normalized)**3 * points[0][1] +
                        3 * (1 - t_normalized)**2 * t_normalized * points[2][1] +
                        3 * (1 - t_normalized) * t_normalized**2 * points[3][1] +
                        t_normalized**3 * points[1][1])
                curve_points.append((x, y))
            
            pygame.draw.lines(screen, (128, 128, 128), False, curve_points, 2)

    def draw(self, screen):
        dot_radius = 10

        # Draw forrests
        for x, y in self.forrests:
            pygame.draw.circle(screen, (34, 139, 34), (x, y), dot_radius)  # Dark Green

        # Draw rivers
        for points in self.rivers:
            # pygame.draw.circle(screen, (128, 128, 128), points[0], dot_radius)
            # pygame.draw.circle(screen, (128, 128, 128), points[-1], dot_radius)
            pygame.draw.lines(screen, (128, 128, 128), False, points, 2)
        # Draw towns
        for x, y in self.towns:
            pygame.draw.circle(screen, (255, 0, 0), (x, y), dot_radius)  # Red

        # Draw roads
        for (x1, y1), (x2, y2) in self.roads:
            pygame.draw.circle(screen, (139, 69, 19), (x1, y1), dot_radius)  # Saddle Brown
            pygame.draw.circle(screen, (139, 69, 19), (x2, y2), dot_radius)  # Saddle Brown
            pygame.draw.line(screen, (139, 69, 19), (x1, y1), (x2, y2), 2)  # Saddle Brown

        # Draw supply depots
        for x, y in self.supply_depots:
            pygame.draw.circle(screen, (255, 255, 0), (x, y), dot_radius)  # Yellow


# def check_intersection(point, river):
#     for i in range(len(river) - 1):
#         line_start = river[i]    
#         line_end = river[i + 1]
#         print(intersect(point, (point[0] + 1, point[1]), line_start, line_end),point ,(point[0] + 1, point[1]), line_start, line_end)
#         if intersect(point, (point[0] + 1, point[1]), line_start, line_end):
#             return True
#     return False

# def intersect( p1, p2, p3, p4):
#     def orientation(p, q, r):
       
#         val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
#         if val == 0:
#             return 0
#         return 1 if val > 0 else 2

    # o1 = orientation(p1, p2, p3)
   
    # o2 = orientation(p1, p2, p4)
    
    # o3 = orientation(p3, p4, p1)
    
    # o4 = orientation(p3, p4, p2)
   
    # if o1 != o2 and o3 != o4:
    #     if min(p1[0], p2[0]) <= max(p3[0], p4[0]) and min(p3[0], p4[0]) <= max(p1[0], p2[0]) and \
    #     min(p1[1], p2[1]) <= max(p3[1], p4[1]) and min(p3[1], p4[1]) <= max(p1[1], p2[1]):
    #         return True

    # return False