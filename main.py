import os
import shutil
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import imageio


class Coord:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other: "Coord"):
        return Coord(
            self.x + other.x, self.y + other.y, self.z + other.z
        )

    def __sub__(self, other: "Coord"):
        return Coord(
            self.x - other.x, self.y - other.y, self.z - other.z
        )

    def __mul__(self, constant):
        return Coord(self.x * constant, self.y * constant, self.z * constant)

    def __iadd__(self, other: "Coord"):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other: "Coord"):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __neg__(self):
        return Coord(-self.x, -self.y, -self.z)

    def __eq__(self, other: "Coord"):
        return (
            self.x == other.x and self.y == other.y and self.z == other.z
        )

    def __ne__(self, other: "Coord"):
        return not (self == other)

    def distance(self, other: "Coord"):
        return np.linalg.norm(
            [self.x - other.x, self.y - other.y, self.z - other.z]
        )


class Sensor:
    def __init__(
        self,
        sensor_id: int,
        sensor_type: str,
        true_location: Coord,
        distance_range: float,
        neighbors: list[Sensor] = [],
        **kwargs,
    ) -> None:
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

    def updateLocation(self, timestep: float) -> None:
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

    def updateNeighbors(self, anchors: list[Sensor], tags: list[Sensor], tagcomm: bool = True) -> None:
        self.neighbors = {}
        for anchor in anchors:
            if self.true_location.distance(anchor.true_location) < self.distance_range:
                self.neighbors[anchor.sensor_id] = self.distance(anchor)
        if tagcomm:
            for tag in tags:
                if (
                    self.true_location.distance(tag.true_location) < self.distance_range
                    and self.sensor_id != tag.sensor_id
                ):
                    self.neighbors[tag.sensor_id] = self.distance(tag)

    def updateUncertainty(self) -> None:
        self.uncertainty *= 1.02 ** (3 - len(self.neighbors))

    def distance(self, other: Sensor) -> float:
        return self.true_location.distance(other.true_location)


def generate_video(frames_dir: str, output_path: str, fps: int = 20, label: str = "2x"):
    frames = sorted(os.listdir(frames_dir))
    images = []

    for fname in frames:
        if fname.endswith(".jpg"):
            img_path = os.path.join(frames_dir, fname)
            img = Image.open(img_path).convert("RGB")

            # Add 2x label in top-left
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            draw.text((10, 10), label, fill="white", font=font)

            images.append(np.array(img))

    imageio.mimsave(output_path, images, fps=fps)


def main(tagcomm: bool = True, *args, **kwargs) -> None:
    # Output directories
    output_dir = "./results/tagcomm" if tagcomm else "./results/notagcomm"
    frames_dir = os.path.join(output_dir, "frames")

    # Clear old outputs
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(frames_dir, exist_ok=True)

    # Simulation parameters
    timestep = kwargs.get("timestep", 0.1)
    final_time = kwargs.get("final_time", 10)
    sensing_radius = kwargs.get("sensing_radius", 5)

    # Initialize sensors
    anchors, tags = [], []
    if "anchor_locations" in kwargs:
        anchor_locations = [
            Coord(loc[0], loc[1], loc[2]) for loc in kwargs["locations"]
        ]
    else:
        anchor_locations = [
            Coord(0.2, 0.2),
            Coord(4, 0.2),
            Coord(3, 9.8),
            Coord(9.8, 6),
            Coord(9.8, 9.8),
            Coord(0.2, 5),
        ]
    if "tag_locations" in kwargs:
        tag_locations = [
            Coord(loc[0], loc[1], loc[2]) for loc in kwargs["tag_locations"]
        ]
    else:
        tag_locations = [
            Coord(1, 2),
            Coord(5, 5),
            Coord(9, 1),
        ]
    anchor_points = ["rx", "bx", "gx", "mx", "kx", "yx"]
    tag_points = ["ro", "go", "bo"]
    if "tag_velocities" in kwargs:
        tag_velocities = [Coord(v[0], v[1], v[2]) for v in kwargs["tag_velocities"]]
    else:
        tag_velocities = [Coord(0.2, 0.5), Coord(-0.3, 0.4), Coord(0.1, 0.7)]
    if "tag_lb_limits" in kwargs:
        tag_lb_limits = [
            Coord(loc[0], loc[1], loc[2]) for loc in kwargs["tag_lb_limits"]
        ]
    else:
        tag_lb_limits = [Coord(1, 1), Coord(7, 6), Coord(3, 0.5)]
    if "tag_rt_limits" in kwargs:
        tag_rt_limits = [
            Coord(loc[0], loc[1], loc[2]) for loc in kwargs["tag_rt_limits"]
        ]
    else:
        tag_rt_limits = [Coord(5, 7), Coord(10, 9), Coord(9.5, 5.5)]
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

    for t_index, t in enumerate(np.arange(0, final_time, timestep)):
        print(f" Processing timestep {t_index + 1}/{int(final_time / timestep)}", end="\r")
        fig, ax = plt.subplots()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

        for i, anchor in enumerate(anchors):
            ax.plot(anchor.true_location.x, anchor.true_location.y, anchor_points[i])

        for tag in tags:
            tag.updateLocation(timestep)

        for i, tag in enumerate(tags):
            tag.updateNeighbors(anchors, tags, tagcomm)
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

        sim_path = os.path.join(output_dir, "sim.mp4")
        generate_video(frames_dir, sim_path, fps=20, label="2x")


if __name__ == "__main__":
    timestep = 0.1
    final_time = 10
    sensing_radius = 7.5
    for tagcomm in [True, False]:
        print(f"Running simulation with tagcomm = {tagcomm}")
        main(
            tagcomm=tagcomm,
            timestep=timestep,
            final_time=final_time,
            sensing_radius=sensing_radius,
        )
        print("\n")
