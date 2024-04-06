'''
Filename: pathfinding
Author: Nathan D (nathan.delcampo@digipen.edu)
Date: 3/14/24

Desc: Class for creating paths for ship and asteroids

'''
from typing import Dict, Tuple
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import Polygon
from math import sqrt, cos, sin
import numpy as np

class PathFinding:
    """PathFinding class that creats a path from a given asteroid and ship,
       then creats a Dictionary with all found paths

    Returns:
        (Dict or Path): A Dictionary of all the Path objects ( PathFinding() ) or
                        you can get a single class Object with PathFinding(index)
    """
         

    ##############################################################
    class __Path:
        """
        Desc: Path class contains relevant data about the path generated including
            collision, the path itself, it's area, estimated time to collsion
        """
        def __init__(
            self,
            line: Polygon,
            collision: Polygon = None,
            area: float = None,
            time: float = None,
        ):
            self.__line = line  # Line is to be a POLYGON of the path of the asteroid
            self.__collision = (
                # Colllision is the POLYGON of the collision (MAY BE NULL)
                collision
            )
            # AREA is to be a number (float) of the area of the collision (MAY BE NULL)
            self.__area = area
            # TIME is to be a estimate (float) of the time to collide with the ship
            self.__time = time

        @property
        def collision(self):
            return self.__collision

        @property
        def line(self):
            return self.__line

        @property
        def area(self):
            return self.__area

        @property
        def time(self):
            return self.__time

        def __call__(self) -> Dict:
            return {
                "line": self.__line,
                "collision": self.__collision,
                "area": self.__area,
                "time": self.__time,
            }

    ##############################################################
    def __init__(self, map_size: tuple = (1000,800)):
        self.paths = {}
        self.map_size = map_size

        # create map edge lines
        edge1 = LineString([(0,0), (map_size[0], 0)])
        edge2 = LineString([(map_size[0], 0), map_size])
        edge3 = LineString([map_size, (0, map_size[1])])
        edge4 = LineString([(map_size[1], 0), (0,0)])

        self.edges = [edge1, edge2, edge3, edge4]

    def __call__(self, index=None, call=False):
        '''
        Desc: Gives the path of a certain index

        Parameters: index - The index of the path in the 'paths' dict
                    call  - Specifies if using index

        Return: Returns None if no paths or a Path object if exists
        '''
        if len(self.paths) > 0:
            if index != None:
                if call:
                    return self.paths[index]()
                else:
                    return self.paths[index]
            else:
                return self.paths
            return None
        
    def __get_path(self, x1, y1, x2, y2, width) -> LineString:
        '''
        Desc: Creates a path using shapely linestring and buffering
            at width

        Parameters: x1 - The x pos of the start point
                    y1 - The y pos of the start point
                    x2 - The x pos of the endpoint
                    y2 - The y pos of the endpoint
                    width - The width to be buffered to

        Return: A shapely linestring 
        '''
        return LineString([(x1, y1), (x2, y2)]).buffer(width)

    def __get_path_split(self, x1, y1, x2, y2, width):
        '''
        DESC: Given two points in a 2d space, create a polygon representing
            the path between those two points, wrapping around the edges of the screen 
            as required

        RETURNS: A list containing the polygons
        '''
        # create empty list for appending of new lines
        lines = []

        # variables for first line
        start = (x1, y1)
        end = (x2, y2)
        line = LineString([start, end])

        # loop until break clause is reached 
        while(1):
            # check for intersection against map edge lines
            for edge in self.edges:
                if not (line.intersection(edge).is_empty):
                    # set to some value to save
                    #print(line.intersection(edge))
                    #print(edge)
                    newEnd = line.intersection(edge)
                    # check if intersection is the start or end points
                    if not (newEnd == Point(line.coords[0]) or newEnd == Point(line.coords[1])):
                        print(newEnd)
                        print(Point(line.coords[0]))
                        print(newEnd == line.coords[0])

                        # if not start or end points then append to list and break
                        lines.append(LineString([currentStart, newEnd]).buffer(width))
                        break
                    else:

                        # reset value to prevent looping
                        newEnd = Point()

            # if edge was touched then split line
            if not (newEnd.is_empty):
                # get new endpoint in coords
                newEnd = [newEnd.x, newEnd.y]
                currentStart = newEnd

                # adjust line endpoint and get new start point
                for idx, pos in enumerate(start):
                    # check against both map edges
                    # print(idx)
                    bound = self.map_size[idx]
                    # print(bound)
                    offset = bound - pos
                    # print(offset)

                    # find new start point
                    if (currentStart[idx] % bound == 0):
                        print("CURRENT START: ", currentStart)
                        currentStart[idx] = abs(newEnd[idx] - bound)
                        print("CURRENT START: ", currentStart)
                        print(bound)

                    # find new endpoint
                    if offset < 0 or offset > bound:
                        # adjust position to other side 
                        start[idx] += bound * np.sign(offset)
                        break

                # get new line 
                line = LineString([currentStart, start])
                print(line)

                # set to empty point to remove data
                newEnd = Point()
            else:
                # append last line to list and break from loop
                lines.append(line.buffer(width))
                break
        
        return lines

    def __circle_line_collision(self, circle, line, radius):
        '''
        Desc: Creates a cricle using shapely given a point and then
            checks it with a line

        Parameters: circle - The center of a circle to check collsion
                    line - The line to check collision with
                    radius - The radius of the cricle

        Return: A multipoint or point object representing the collision points
        '''
        # create circle polygon with point and boundary
        center = Point(circle[0], circle[1])
        circleObject = center.buffer(radius)

        # will return MULTIPOINT or POINT
        return circleObject.intersection(line)

    def path_find_ship(self, ship: Dict, dist):
        '''
        Desc: Creates a path in front and behind the ship based on distance given

        Parameters: ship - The ship object
                    dist - The dist of the path

        Return: The path of the ship
        '''
        # find pos
        shipPos = ship["position"]

        # get vector in both directions
        shipAngle = ship["angle"]

        # mod angle by 90 for math
        adjustedAngle = shipAngle % 90
        forwardVector = (dist * cos(adjustedAngle), dist * sin(adjustedAngle))

        # adjust values based on quadrant being faced
        if (shipAngle > 270):
            forwardVector[1] *= -1
        else:
            if (shipAngle > 180):
                forwardVector[0] *= -1
                forwardVector[1] *= -1
            else:
                if (shipAngle > 90):
                    forwardVector[0] *= -1

        # get start and end pos of ship based on vector
        backPos = (shipPos[0] - forwardVector[0], shipPos[1] - forwardVector[1])
        frontPos = (shipPos[0] + forwardVector[0], shipPos[1] + forwardVector[1])

        
        # return 
        return self.path_find(backPos[0], backPos[1], frontPos[0], frontPos[1], ship["radius"])

    # Find path for asteroid after 10 seconds, find time from ship if colliding
    def path_find(self, asteroid: Dict, ship: Dict, id: int):
        """Finds the path for the asteroid after 10 seconds,
           and finds time if ship is colinging

        Args:
            asteroid (Dict): List of properties for asteroid
            ship (Dict): List of ship properties for ship

        Returns:
            Path: current asteroid path
        """
        # get asteroid data
        # static values rn because im stupid
        asteroidPos = asteroid["position"]
        asteroidVelocity = asteroid["velocity"]
        asteroidRadius = asteroid["radius"]
        shipPos = ship["position"]

        # Asteroid end position after 10 seconds
        # Does velocity work in units/s / is *10 valid?
        asteroidEndPos = (
            asteroidPos[0] + (asteroidVelocity[0] * 10),
            asteroidPos[1] + (asteroidVelocity[1] * 10),
        )

        # call get path as polygon
        line = self.__get_path(
            asteroidPos[0],
            asteroidPos[1],
            asteroidEndPos[0],
            asteroidEndPos[1],
            asteroid["radius"],
        )

        # find collision
        collision = self.__circle_line_collision(shipPos, line, 25)

        # If colliding
        if ~collision.is_empty:
            # Get area of collision
            area = collision.area

            # Shapely point at start
            endPoint = Point(asteroidPos[0], asteroidPos[1])

            # Find estimated time to collision
            timeToCollision = collision.distance(endPoint) / sqrt(
                asteroidVelocity[0] ** 2 + asteroidVelocity[1] ** 2
            )

            asteroidPath = self.__Path(line, collision, area, timeToCollision)
        else:
            # Create path class with no collision
            asteroidPath = __Path(line, None, None, None)

        if id in self.paths.keys():
            self.paths.pop(id)

        self.paths[id] = asteroidPath
