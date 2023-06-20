from distutils.core import setup
setup(
  name = 'scrappeycom',         # How you named your package folder (MyLib)
  packages = ['scrappeycom'],   # Chose the same as "name"
  version = '0.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'An API wrapper for Scrappey.com written in Python (cloudflare bypass & solver)',   # Give a short description about your library
  author = 'dormic97',                   # Type in your name
  author_email = 'crozz-boy@hotmail.com',      # Type in your E-Mail
  url = 'https://github.com/pim97/scrappey-wrapper-python',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/pim97/scrappey-wrapper-python/archive/refs/tags/v_01.tar.gz',    # I explain this later on
  keywords = ["captcha", "shape", "web-scraping", "data-extraction", "akamai", "captcha-solver", "incapsula", "queue-it", "scraping-framework", "datadome", "scraping-tool", "cloudflare-bypass", "web-scraping-solution", "scraping-library", "cloudflare-anti-bot", "scraping-service", "web-data-extraction", "anti-bot-api", "perimetex"],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)