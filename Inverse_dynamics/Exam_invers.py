import numpy as np
import os
from simulator import Simulator
from pathlib import Path
from typing import Dict
import pinocchio as pin
import matplotlib.pyplot as plt
from scipy.linalg import logm

current_dir = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(current_dir, "robots/universal_robots_ur5e/ur5e.xml")
model_1 = pin.buildModelFromMJCF(xml_path)
data_1 = model_1.createData()

times_1 = []
positions_1 = []
velocities_1 = []
control_1 = []
error_1 = []
s_1 = []
    
def plot_results(times: np.ndarray, positions: np.ndarray, velocities: np.ndarray, torque: np.ndarray, error: np.ndarray):
    """Plot and save simulation results."""
    # Joint positions plot
    plt.figure(figsize=(10, 6))
    for i in range(positions.shape[1]):
        plt.plot(times, positions[:, i], label=f'Joint {i+1}')
    plt.xlabel('Time [s]')
    plt.ylabel('Joint Positions [rad]')
    plt.title('Joint Positions over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('logs/plots/Exam_inv_pos.png')
    plt.close()
    
    # Joint velocities plot
    plt.figure(figsize=(10, 6))
    for i in range(velocities.shape[1]):
        plt.plot(times, velocities[:, i], label=f'Joint {i+1}')
    plt.xlabel('Time [s]')
    plt.ylabel('Joint Velocities [rad/s]')
    plt.title('Joint Velocities over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('logs/plots/Exam_inv_vel.png')
    plt.close()

    plt.figure(figsize=(10, 6))
    for i in range(velocities.shape[1]):
        plt.plot(times, torque[:, i], label=f'Joint {i+1}')
    plt.xlabel('Time [s]')
    plt.ylabel('Joint Torque [Nm]')
    plt.title('Joint Torque over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('logs/plots/Exam_inv_tor.png')
    plt.close()

    plt.figure(figsize=(10, 6))
    for i in range(positions.shape[1]):
        plt.plot(times, error[:, i], label=f'Joint {i+1}')
    plt.xlabel('Time [s]')
    plt.ylabel('Joint Positions Error [rad]')
    plt.title('Joint Positions Error over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('logs/plots/Exam_inv_err.png')
    plt.close()

def traj(t):
    R = 0.08
    X = np.array([0.15+R*np.sin(2*np.pi*t/2), -0.7+R*np.cos(2*np.pi*t/2), 0.5+R*np.cos(2*np.pi*t/2), 0, 0., -np.pi/2])
    dX = np.array([2*np.pi*R*np.cos(2*np.pi*t/2), -2*np.pi*R*np.sin(2*np.pi*t/2), -R*2*np.pi*np.sin(2*np.pi*t/2), 0, 0, 0])
    ddX = np.array([-((2*np.pi)**2)*R*np.sin(2*np.pi*t/2), -((2*np.pi)**2)*R*np.cos(2*np.pi*t/2), -R*((2*np.pi)**2)*np.cos(2*np.pi*t/2), 0, 0, 0])

    return X, dX, ddX

def joint_controller(q: np.ndarray, dq: np.ndarray, t: float) -> np.ndarray:
    """Example task space controller."""

    times_1.append(t)
    positions_1.append(q)
    velocities_1.append(dq)

    q_d = np.array([-0.7, -1.3, 1., 0., 0., 0.])
    dq_d = np.array([0., 0., 0., 0., 0., 0.])
    ddq_d = np.array([0., 0., 0., 0., 0., 0.])

    # q_d, dq_d, ddq_d = traj(t)

    print(q_d - q)
    error_1.append(q_d - q)

    pin.computeAllTerms(model_1, data_1, q, dq)

    M_h = 0.95*data_1.M
    nle_h = 1.05*data_1.nle
    D_h = np.array([0.6, 0.6, 0.6, 0.2, 0.2, 0.2])
    F_h = np.array([0.4, 0.4, 0.4, 0.05, 0.05, 0.05])

    Kp = 100*np.array([1., 1., 1., 1., 1., 1.])
    Kd = 20*np.array([1., 1., 1., 1., 1., 1.])

    v = ddq_d + Kp*(q_d - q) + Kd*(dq_d - dq)

    tau = M_h@v + nle_h + D_h*dq + F_h*np.sign(dq)

    control_1.append(tau)

    return tau

def main():
    # Create logging directories
    Path("logs/videos").mkdir(parents=True, exist_ok=True)
    
    print("\nRunning task space controller...")
    sim = Simulator(
        xml_path="robots/universal_robots_ur5e/scene.xml",
        enable_task_space=False,
        show_viewer=True,
        record_video=True,
        video_path="logs/videos/Exam_invers_dyn.mp4",
        fps=30,
        width=1920,
        height=1080
    )

    # sim.modify_body_properties(ee_name, mass=3)
    # # Print modified properties
    # props = sim.get_body_properties(ee_name)
    # print(f"\nModified end-effector properties:")
    # print(f"Mass: {props['mass']:.3f} kg")
    # print(f"Inertia:\n{props['inertia']}")

    damping = np.array([0.5, 0.5, 0.5, 0.1, 0.1, 0.1])  # Nm/rad/s
    sim.set_joint_damping(damping)
    
    # Set joint friction (example values, adjust as needed)
    friction = np.array([0.5, 0.5, 0.5, 0.1, 0.1, 0.1])  # Nm
    sim.set_joint_friction(friction)

    sim.modify_body_properties("end_effector", mass=4)

    sim.set_controller(joint_controller)

    sim.run(time_limit=2.0)

if __name__ == "__main__":
    # print(current_dir)
    main() 

    times_1 = np.array(times_1)
    positions_1 = np.array(positions_1)
    velocities_1 = np.array(velocities_1)
    control_1 = np.array(control_1)
    error_1 = np.array(error_1)

    plot_results(times_1, positions_1, velocities_1, control_1, error_1)