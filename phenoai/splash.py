""" This module implements functions to show the splash text and do an update check for PhenoAI """

first_start = True

def splash(do_update_check=True):
	""" Makes the splash text

	This function will only show the splash screen once, even when called multiple times. In order to reset this behaviour, overwrite the first_start parameter in this module.

	Parameters
	----------
	do_update_check: boolean (optional, default=True)
		If set to True, after the splash screen the check_updates() function in this module will be called."""

	# Splash screens and welcome
	global first_start
	if first_start:
		from . import __versiondate__, __versionnumber__, __version__

		first_start = False
		
		# Print welcome screen
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
      ,,,,,,%@@ ,,,,,,,,,,,,,,,,,..........,,,,,,,,,,,,,,,,,, ,,,.,,         
%@@@@@@@@ ,,%@@ ,,,,,,,,,,,,,,,,,..........,,,,,,,,,,,,,,,,, @@@@@,    %@@%  
%@@%   @@@,,%@@ @@@@@ ,, @@@@@@% ..@@@ @@@@,.,, @@@@@@@ ,,,,&@@.@@@    %@@%  
%@@@   @@@ ,%@@@ .%@@#, @@@...@@@ .@@@@..%@@., @@@,,,@@@ ,, @@&  @@@   %@@%
%@@@@@@@@   %@@   ,@@%,,@@@@@@@@@ .@@@...,@@,,%@@,,,,%@@,, @@@@@@@@@;  %@@%  
%@@%        %@@   ,@@%  @@@........@@@...,@@,,,@@@,,,@@@  @@@,,,,,@@@  %@@%  
%@@%        %@@   ,@@%    @@@@@&...@@@...,@@,,,. @@@@@   ;@@#      @@@ %@@%  
                                   ,.......                                  



{:<32}{:>43}
{:<32}{:>43}
{:<32}{:>43}
{:<75}
{:<32}{:>43}\n""".format("Bob Stienen", "Version {}".format(__version__), "Sascha Caron", "Versionnumber: {}".format(__versionnumber__), "Roberto Ruiz de Austri", "Version date: {}".format(__versiondate__), "Jong Soo Kim", "Krzysztof Rolbiecki", "Contact: b.stienen@science.ru.nl"))
		if do_update_check:
			check_updates()
			
def check_updates():
	""" Calls updatechecker.check_phenoai_update() and shows output """

	# Check for package updates
	from . import updatechecker
	error, updatable, txt = updatechecker.check_phenoai_update()
	if not error:
		print(txt+"\n")
	else:
		print("Could not check for updates, because: "+txt+"\n")