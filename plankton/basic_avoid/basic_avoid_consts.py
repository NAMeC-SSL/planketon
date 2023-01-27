# warning : grSim gives distances in millimeters at the moment

robot_radius = 0.12  # measured using my cursor on grSim
danger_k = 0.3  # magic number, TBD properly

# See description file for explanations
danger_circle_radius = 2 * robot_radius + danger_k
