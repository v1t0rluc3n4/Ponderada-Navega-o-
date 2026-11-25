from setuptools import find_packages, setup

setup(
    name='cg_navigation', version='1.0.0', packages=find_packages(),
    data_files=[('share/ament_index/resource_index/packages', ['resource/cg_navigation']),
                ('share/cg_navigation', ['package.xml'])],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='Vitor Lopes Lucena', maintainer_email='vitor@example.com',
    description='BFS navigation and sensor-only maze mapping', license='MIT',
    entry_points={'console_scripts': [
        'navigate = cg_navigation.ros_node:main',
        'validate_offline = cg_navigation.offline:main']},
)
