""" PhenoAI allows users to import and use trained sklearn estimators and
keras models out-of-the-box in existing workflows. Once loaded, PhenoAI
implements methods to call and compare multiple AInalyses and run PhenoAI
in a server-client structure.

Generalization over machine learning methods is a key concept of PhenoAI: it
depends as little as possible on the loaded estimator. Although PhenoAI as a
package is focussed on applications within data analysis in high energy
physics, the interface is also usable outside of this field.

To load estimators, they have to be wrapped in a PhenoAI-specific format: an
AInalysis. The .maker module allows the user to store estimators in this
format."""

from phenoai.__version__ import __version__, __versionnumber__, __versiondate__, __author__
from phenoai.core import PhenoAI
from phenoai.client import PhenoAIClient
from phenoai.ainalyses import AInalysis


try:
    splashed
except Exception:
    splashed = True
    print("""
                               &&&&&&&&&&&&&
                            &&&&&&&&&&&&&&&&&&&
                          &&&&&&&&&&&&&&&&&&&&&&&
                         &&&&&&&&&&:::::&&&&&&&&&&
                         &&&&&&&&&&:::::&&&&&&&&&&
                  #######################################
                  #######################################
                  #######           ###           ######
                   #####             #             #####
          &&&&&&   #####  OOO        #  OOO        #####&&&&&&&&&&,,,
     ,,,&&&&&&&&&&&&&###  OOO        #  OOO        &&&&&&&&&&&&,,,,,,
     ,,,,,,,,,,,,,&&&&&&&&&OO        #  OOO   &&&&&&&&&&&&,,,,,,,,,,,
     ,,,,,,,,,,,,,,,,,,,,,&&&&&&&&&&&&&&&&&&&&&&&&&,,,,,,,,,,,,,,,,,,
     ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,&&&&&&&&&,,,,,,,,,,,,,,,,,,,,,,,,,
      ,,,,,,,,,,,,,,,,,,,,,,,,,,,..........,,,,,,,,,,,,,,,,,,,,,,,,,
%@@@@@@@@ ,,%@@ ,,,,,,,,,,,,,,,,,..........,,,,,,,,,,,,,,,,,, ,,,.,,
%@@%   @@@,,%@@ ,,,,,,,,,,,,,,,,,..........,,,,,,,,,,,,,,,,, @@@@@,    %@@%
%@@%   @@@,,%@@@@@@@@ ,, @@@@@@% ..@@@ @@@@,.,, @@@@@@@ ,,,,&@@.@@@    %@@%
%@@@@@@@@  ,%@@@ .%@@#, @@@...@@@ .@@@@..%@@., @@@,,,@@@ ,, @@&  @@@   %@@%
%@@%        %@@   ,@@%,,@@@@@@@@@ .@@@...,@@,,%@@,,,,%@@,, @@@@@@@@@;  %@@%
%@@%        %@@   ,@@%  @@@........@@@...,@@,,,@@@,,,@@@  @@@,,,,,@@@  %@@%
%@@%        %@@   ,@@%    @@@@@&...@@@...,@@,,,. @@@@@   ;@@#      @@@ %@@%
                                   ,.......



{:<32}{:>43}
{:<32}{:>43}
{:<32}{:>43}
{:<75}
{:<32}{:>43}\n""".format("Bob Stienen",
                         "Version {}".format(__version__),
                         "Sascha Caron",
                         "Versionnumber: {}".format(__versionnumber__),
                         "Roberto Ruiz de Austri",
                         "Version date: {}".format(__versiondate__),
                         "Jong Soo Kim", "Krzysztof Rolbiecki",
                         "Contact: b.stienen@science.ru.nl"))


def check_updates():
    """ Calls :func:`phenoai.updatechecker.check_phenoai_update` and shows
    output """

    # Check for package updates
    from phenoai import updatechecker
    error, _, txt = updatechecker.check_phenoai_update()
    if not error:
        print(txt+"\n")
    else:
        print("Could not check for updates, because: "+txt+"\n")
