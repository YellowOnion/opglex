from distutils.core import setup

files = ['shaders/*']
setup(  name = 'opglex',
		version = '0.0.1',
		description = 'Openglex is a post-apocalyptic racing game',
		author = "Daniel B Hill",
		author_email = "daniel@enemyplanet.geek.nz",
		url	= "null",
		packages = ['opglex'],
		package_data = { 'opglex': files },
		scripts = ['nehe-1.py'],
		long_description = """race till you run out of oil""",
)
