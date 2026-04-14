from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'roomba_logic'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='xamacardoso',
    maintainer_email='contato.xcardoso@gmail.com',
    description='Controle do Roomba para TCC',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
		'girar = roomba_logic.turtle_circulo:main',
        'detector = roomba_logic.detector_aruco:main',
        # 'brain = roomba_logic.brain_node:main',
        'mission_control = roomba_logic.mission_control:main',
        'draw_track = roomba_logic.draw_track:main',
        ],
    },
)
