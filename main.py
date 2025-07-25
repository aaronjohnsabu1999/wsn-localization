import os
import numpy as np
from matplotlib import pyplot as plt


class Coord:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, coordinate: "Coord"):
        return Coord(
            self.x + coordinate.x, self.y + coordinate.y, self.z + coordinate.z
        )

    def __sub__(self, coordinate: "Coord"):
        return Coord(
            self.x - coordinate.x, self.y - coordinate.y, self.z - coordinate.z
        )

    def __mul__(self, constant):
        return Coord(self.x * constant, self.y * constant, self.z * constant)

    def __iadd__(self, coordinate: "Coord"):
        self.x += coordinate.x
        self.y += coordinate.y
        self.z += coordinate.z
        return self

    def __isub__(self, coordinate: "Coord"):
        self.x -= coordinate.x
        self.y -= coordinate.y
        self.z -= coordinate.z
        return self

    def __neg__(self):
        return Coord(-self.x, -self.y, -self.z)

    def __eq__(self, coordinate: "Coord"):
        return (
            self.x == coordinate.x and self.y == coordinate.y and self.z == coordinate.z
        )

    def __ne__(self, coordinate: "Coord"):
        return not (self == coordinate)

    def distance(self, coordinate: "Coord"):
        return np.linalg.norm(
            [self.x - coordinate.x, self.y - coordinate.y, self.z - coordinate.z]
        )


class Sensor:
    def __init__(
        self,
        sensor_id,
        sensor_type,
        true_location,
        distance_range,
        neighbors=[],
        **kwargs,
    ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.true_location = true_location
        self.distance_range = distance_range
        self.neighbors = neighbors
        if self.sensor_type == "MOBILE":
            self.velocity = kwargs["velocity"]
            self.lblimit = kwargs["lblimit"]
            self.rtlimit = kwargs["rtlimit"]
            self.uncertainty = kwargs["uncertainty"]

    def locationUpdate(self, timestep):
        if self.sensor_type != "MOBILE":
            raise TypeError("Location Update is not possible for immobile sensor")
        if self.true_location.x < self.lblimit.x:
            self.velocity.x = abs(self.velocity.x)
        elif self.true_location.x > self.rtlimit.x:
            self.velocity.x = -abs(self.velocity.x)
        if self.true_location.y < self.lblimit.y:
            self.velocity.y = abs(self.velocity.y)
        elif self.true_location.y > self.rtlimit.y:
            self.velocity.y = -abs(self.velocity.y)
        self.true_location += self.velocity * timestep

    def updateNeighbors(self, anchors, tags, taglinks):
        self.neighbors = {}
        for anchor in anchors:
            if self.true_location.distance(anchor.true_location) < self.distance_range:
                self.neighbors[anchor.sensor_id] = self.distance(anchor)
        if taglinks:
            for tag in tags:
                if (
                    self.true_location.distance(tag.true_location) < self.distance_range
                    and self.sensor_id != tag.sensor_id
                ):
                    self.neighbors[tag.sensor_id] = self.distance(tag)

    def updateUncertainty(self):
        length = len(self.neighbors)
        if length <= 2:
            self.uncertainty *= 1.02
        elif length == 3:
            self.uncertainty *= 1.002
        else:
            self.uncertainty /= 1.02 ** (length - 3)

    def distance(self, sensor2):
        return self.true_location.distance(sensor2.true_location)


def main(timestep, final_time, sensing_radius, taglinks=True):
    anchors, tags = [], []
    anchor_locations = [
        Coord(0.2, 0.2),
        Coord(4, 0.2),
        Coord(3, 9.8),
        Coord(9.8, 6),
        Coord(9.8, 9.8),
        Coord(0.2, 5),
    ]
    anchor_points = ["rx", "bx", "gx", "mx", "kx", "yx"]
    tag_locations = [Coord(1, 2), Coord(5, 5), Coord(9, 1)]
    tag_velocities = [Coord(0.2, 0.5), Coord(-0.3, 0.4), Coord(0.1, 0.7)]
    tag_lb_limits = [Coord(1, 1), Coord(7, 6), Coord(3, 0.5)]
    tag_rt_limits = [Coord(5, 7), Coord(10, 9), Coord(9.5, 5.5)]
    tag_points = ["ro", "go", "bo"]
    tag_lines = ["r-", "g-", "b-"]

    for i in range(len(anchor_locations)):
        anchors.append(Sensor(f"A{i}", "FIXED", anchor_locations[i], sensing_radius))
    for i in range(len(tag_locations)):
        tags.append(
            Sensor(
                f"T{i}",
                "MOBILE",
                tag_locations[i],
                sensing_radius,
                velocity=tag_velocities[i],
                lblimit=tag_lb_limits[i],
                rtlimit=tag_rt_limits[i],
                uncertainty=70,
            )
        )

    output_dir = "./results/plots"
    if taglinks:
        output_dir += "/taglinks"
    else:
        output_dir += "/notaglinks"
    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)

    for t_index, t in enumerate(np.arange(0, final_time, timestep)):
        fig, ax = plt.subplots()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

        for i, anchor in enumerate(anchors):
            ax.plot(anchor.true_location.x, anchor.true_location.y, anchor_points[i])

        for tag in tags:
            tag.locationUpdate(timestep)

        for i, tag in enumerate(tags):
            tag.updateNeighbors(anchors, tags, taglinks)
            tag.updateUncertainty()
            loc1 = tag.true_location
            ax.plot(loc1.x, loc1.y, tag_points[i], markersize=tag.uncertainty)
            for neighbor_id in tag.neighbors:
                if neighbor_id.startswith("A"):
                    loc2 = next(
                        a.true_location for a in anchors if a.sensor_id == neighbor_id
                    )
                    ax.plot([loc1.x, loc2.x], [loc1.y, loc2.y], tag_lines[i])
                else:
                    loc2 = next(
                        tg.true_location for tg in tags if tg.sensor_id == neighbor_id
                    )
                    ax.plot([loc1.x, loc2.x], [loc1.y, loc2.y], "y-")

        plt.savefig(f"{frames_dir}/frame_{t_index:04d}.jpg")
        if t_index == 0:
            plt.savefig(f"{output_dir}/start.jpg")
        if t_index == int(final_time / timestep) - 1:
            plt.savefig(f"{output_dir}/end.jpg")
        plt.close(fig)


if __name__ == "__main__":
    timestep = 0.1
    final_time = 20
    sensing_radius = 7
    for taglinks in [True, False]:
        print(f"Running simulation with taglinks = {taglinks}")
        main(
            timestep=timestep,
            final_time=final_time,
            sensing_radius=sensing_radius,
            taglinks=taglinks,
        )
