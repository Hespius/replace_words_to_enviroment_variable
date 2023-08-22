import os
import re
import shutil
import ast

def find_strings_in_python_file(content):
    strings = []
    
    tree = ast.parse(content)
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Str):  # Verifica se o nó é uma string
            strings.append((node.lineno, node.s))
    
    return strings

def find_and_replace_strings(file_path, target_strings, output_dir):
    # Criar diretório de saída se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ocorrencias = []

    # Percorrer arquivos no diretório
    for root, _, files in os.walk(file_path):
        for file_name in files:
            if file_name.endswith((".py", ".sh")):
                file_path = os.path.join(root, file_name)

                # Procurar por ocorrências das palavras alvo
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, start=1):
                        for target in target_strings:
                            if target in line:
                                ocorrencias.append((file_name, target, line_num))

                # Escrever ocorrências em um arquivo de texto
                output_file = os.path.join(output_dir, "ocorrencias.txt")
                with open(output_file, 'w') as f:
                    for occurrence in ocorrencias:
                        f.write(f"Arquivo: {occurrence[0]}, Palavra: {occurrence[1]}, Linha: {occurrence[2]}\n")

                # Criar cópia do arquivo com substituições
                output_file_path = os.path.join(output_dir, file_name)
                shutil.copyfile(file_path, output_file_path)

                # Realizar substituições nas cópias
                with open(output_file_path, 'r+') as f:
                    content = f.read()

                    for target in target_strings:
                        if file_name.endswith(".sh"): # Linha de arquivo .sh
                            content = re.sub(re.escape(target), f"${{{target}}}", content)
                            
                            # Adiciona variavel de ambiente no inicio do codigo
                            content = f"{target}=\n" + content

                        elif file_name.endswith(".py"):
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Str):
                                    original_string = node.s
                                    if (f"'''{original_string}'''") in content: # Linha de arquivo .py com três aspas simples
                                        modified_string  = original_string.replace(target, f"''' + {target} + '''")
                                        content = content.replace(f"'''{original_string}'''", f"'''{modified_string}'''")
                                    elif (f'"""{original_string}"""') in content: # Linha de arquivo .py com três aspas dupla
                                        modified_string  = original_string.replace(target, f'""" + {target} + """')
                                        content = content.replace(f'"""{original_string}"""', f'"""{modified_string}"""')
                                    elif (f"'{original_string}'") in content: # Linha de arquivo .py com aspas simples
                                        modified_string  = original_string.replace(target, f"' + {target} + '")
                                        content = content.replace(f"'{original_string}'", f"'{modified_string}'")
                                    else: # Linha de arquivo .py com aspas dupla
                                        modified_string  = original_string.replace(target, f'" + {target} + "')
                                        content = content.replace(f'"{original_string}"', f'"{modified_string}"')

                            content = f"{target} = os.environ['{target}']\n" + content
                        else:
                            content = content
                        

                        f.seek(0)
                        f.write(content)
                        f.truncate()

if __name__ == "__main__":
    input_directory = input("Digite o caminho do diretório: ")
    target_strings = input("Digite as palavras alvo separadas por espaço: ").split()
    output_directory = "output_files"

    find_and_replace_strings(input_directory, target_strings, output_directory)
    print("Processo concluído. Arquivos de saída e ocorrências estão disponíveis em 'output_files'.")
