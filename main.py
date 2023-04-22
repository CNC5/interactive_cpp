import argparse
import subprocess
import os
import uuid

class interactive_compiler:
    def add_extended_funcs(self):
        extended_functions = 'void print(auto prompt){cout<<prompt<<endl;}'
        self.functions += extended_functions
        self.functions_dict.append('print')

    def __init__(self):
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('-d', '--debug',
                            action='store_true',
                            help='enable debugging',
                            dest='debug',
                            default=False)
        parser.add_argument('-s', '--stripped',
                            action='store_true',
                            help='disable additional helper functions and default namespace',
                            dest='stripped',
                            default=False)
        self.args = parser.parse_args()
        self.includes = '#include <iostream>\nusing namespace std;\n'
        self.func_level = 0
        self.functions = ''
        self.functions_dict = []
        self.vars = ''
        self.vars_dict = []
        self.main = ''
        self.types = ['int', 'string', 'void', 'float', 'char']
        if self.args.stripped:
            self.includes = ''
        else:
            self.add_extended_funcs()

    def compile(self):
        assembled_file = self.includes+'\n'+self.functions+'\nint main(){\n'+\
            self.vars+'\n'+self.main+'\nreturn 0;\n}'
        if self.args.debug:
            print(f'VARS DICT: {self.vars_dict}')
            print(f'FULL FILE:\n{assembled_file}')
        with open('tmp.cpp', 'w') as file:
            file.write(assembled_file)
        filename = str(uuid.uuid4())
        if self.args.debug:
            print('COMPILATION STAGE START:')
        compile_command = ['g++', 'tmp.cpp', '-o', filename]
        if not self.args.debug:
            compile_command.append('-w')
        subprocess.run(compile_command)
        if os.name == "nt":
            name = ".\\" + filename + ".exe"
        else:
            name = "./" + filename
        if os.path.isfile(name):
            if self.args.debug:
                print('COMPILATION STAGE END')
            subprocess.run([name])
            subprocess.run(['rm', name])
        else:
            print('COMPILATION FAILED')
        subprocess.run(['rm', 'tmp.cpp'])

    def include(self, name):
        self.includes += f'#include {name}\n'

    def validate(self, line):
        if line[-1] != ';':
            if line.split(' ')[0] in self.types and '(' in line:
                return line
            else:
                line += ';'
                if self.args.debug:
                    print('VALIDATOR: line completed with ;')
        return line

    def exec_line(self, line):
        first_word = line.split(' ')[0]
        cmd_list = {'reset':    'reset the scope',
                    'scope':    'print the current scope',
                    'add_type': 'add a new var type',
                    'help':     'print help',
                    'debug':    'enable/disable debugging'}
        if not line:
            print('execution complete, exiting')
            exit()
        elif line[0] == '!' and not first_word[1:] in cmd_list:
            print(first_word[1:])
            print(f'{line[1:]} is not a command')
            return
        elif first_word == '!reset':
            self.__init__()
            print('scope reset')
            return
        elif first_word == '!scope':
            print(f'INCLUDES:\n{self.includes}')
            print(f'VARIABLE_TYPES: {self.types}')
            print(f'VARIABLES:\n{self.vars_dict}')
            print(f'FUNCTIONS:\n{self.functions}')
            return
        elif first_word == '!help':
            print('cmd list:')
            for cmd in cmd_list:
                print(f'{cmd}: {cmd_list[cmd]}')
            return
        elif first_word == '!add_type':
            for type in line.split(' ')[1:]:
                if type not in self.types:
                    self.types.append(type)
                else:
                    print('already present')
            return
        elif first_word == '!debug':
            if self.args.debug:
                self.args.debug = False
                print('debugging is now off')
            else:
                self.args.debug = True
                print('debugging is now on')
            return
        elif line in self.vars_dict:
            if self.args.debug:
                print('AUTOPRINTING')
            line = f'cout<<{line}<<endl;'
            self.main += line+'\n'
        elif self.func_level:
            if '}' in line:
                self.func_level -= 1
                self.functions += '}\n'
            else:
                self.functions += self.validate(line)
            return
        elif first_word in self.types:
            if '(' in line:
                self.func_level += 1
                self.functions += line
                self.functions_dict.append(line.split(' ')[1].split('(')[0])
                return
            else:
                var_type, var_name = line.split(' ', 1)
                var_name = var_name.split('=')[0]
                if var_name in self.vars_dict:
                    tmp = self.vars
                    self.vars = ''
                    for x in tmp.split('\n'):
                        if f' {var_name}' not in x:
                            self.vars=self.vars+x+'\n'
                self.vars += f'{self.validate(line)}\n'
                if not var_name in self.vars_dict:
                    self.vars_dict.append(var_name)
                return
        elif first_word == '#include':
            self.includes += line
            return
        else:
            if self.args.debug:
                print('UNRECOGNIZED LINE')
            self.main += self.validate(line)+'\n'
        self.compile()
        self.main = ''

icpp = interactive_compiler()

if __name__ == '__main__':
    default_prompt = '>>> '
    function_prompt = '... '
    print('for help: !help')
    while True:
        if icpp.func_level > 0:
            icpp.exec_line(input(function_prompt))
        else:
            icpp.exec_line(input(default_prompt))

