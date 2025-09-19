# import os
from Models.cls_usuario import Administrador

def exibir_cabecalho(titulo):
    print("\n" + "=" * 60)
    print(f"  {titulo.center(56)}")
    print("=" * 60)


def login(sistema):
    exibir_cabecalho("LOGIN")

    try:
        usuario_id = input("ID de usuário: ").strip()
        if not usuario_id:
            print("ID não pode estar vazio.")
            return None

        senha = input("Senha: ").strip()
        if not senha:
            print("Senha não pode estar vazia.")
            return None

        return sistema.autenticar_usuario(usuario_id, senha)
    except KeyboardInterrupt:
        print("\nOperação Cancelada.")
        return None

def menu_usuario(usuario, sistema):
    while True:
        exibir_cabecalho(f"MENU DO USUÁRIO: {usuario.get_nome()}")

        print("\n1. Reservar Locker")
        print("2. Liberar Locker")
        print("3. Ver Meu Locker")
        print("4. Ver Histórico de Reservas")
        print("5. Alterar Senha")
        print("6. Sair")

        try:
            opcao = input("\nEscolha uma opção (1-6): ").strip()

            if opcao == "1":
                from Core.helper import HelperMenus
                helper = HelperMenus(sistema)
                helper.reservar_locker(usuario)
                input("\nPressione Enter para continuar...")
            elif opcao == "2":
                pass
                # liberar_locker(usuario, sistema)
            elif opcao == "3":
                pass
                # ver_locker(usuario, sistema)
            elif opcao == "4":
                pass
                # usuario.exibir_historico()
            elif opcao == "5":
                pass
                # alterar_senha(usuario, sistema)
            elif opcao == "6":
                print("Retornando ao Menu Principal")
                break
            else:
                print("Opção inválida. Digite um número de 1 a 6.")

        except KeyboardInterrupt:
            break


def menu_administrador(admin, sistema):
    while True:
        exibir_cabecalho(f"MENU DO ADMINISTRADOR: {admin.get_nome()}")

        print("\n1. Adicionar Locker")
        print("2. Colocar Locker em Manutenção")
        print("3. Retirar Locker de Manutenção")
        print("4. Ver Todos os Lockers")
        print("5. Listar Usuários")
        print("6. Forçar Liberação de Locker")
        print("7. Remover Locker")
        print("8. Relatório do Sistema")
        print("9. Sair")

        try:
            opcao = input("\nEscolha uma opção (1-9): ").strip()

            if opcao == "1":
                pass
                # adicionar_locker_admin(admin, sistema)
            elif opcao == "2":
                pass
                # colocar_manutencao_admin(admin, sistema)
            elif opcao == "3":
                pass
                # retirar_manutencao_admin(admin, sistema)
            elif opcao == "4":
                pass
                # listar_lockers_admin(sistema)
            elif opcao == "5":
                pass
                # admin.listar_usuarios_sistema(sistema)
            elif opcao == "6":
                pass
                # forcar_liberacao_admin(admin, sistema)
            elif opcao == "7":
                pass
                # remover_locker_admin(admin, sistema)
            elif opcao == "8":
                pass
                # admin.gerar_relatorio_sistema(sistema)
            elif opcao == "9":
                break
            else:
                print("Opção inválida. Digite um número de 1 a 9.")

        except KeyboardInterrupt:
            break


def menu_principal(sistema):
    while True:
        exibir_cabecalho("SISTEMA DE LOCKERS - BEM-VINDO")

        print("\nEscolha uma opção:")
        print("1. Login")
        print("2. Cadastro")
        print("3. Sair")

        opcao = input("\nDigite sua opção (1-3): ").strip()

        if opcao == "1":
            usuario = login(sistema)
            if usuario:
                if isinstance(usuario, Administrador):
                    menu_administrador(usuario, sistema)
                else:
                    menu_usuario(usuario, sistema)

        elif opcao == "2":
            exibir_cabecalho("AUTENTICAÇÃO DE ADMINISTRADOR")
            print("\nPara cadastrar novos usuários, é necessário autenticação de administrador.")
            usuario = login(sistema)
            
            if usuario:
                if isinstance(usuario, Administrador):
                    print("\nAutenticação de administrador bem-sucedida!")
                    
                    while True:
                        exibir_cabecalho("CADASTRO DE NOVO USUÁRIO")
                        print("\n1. Cadastrar Usuário Comum")
                        print("2. Cadastrar Administrador")
                        print("3. Voltar")
                        
                        tipo = input("\nEscolha o tipo de usuário (1-3): ").strip()
                        
                        if tipo in ["1", "2"]:
                            nome = input("\nDigite o nome do novo usuário: ").strip()
                            senha = input("Digite a senha do novo usuário: ").strip()
                            
                            is_admin = (tipo == "2")
                            novo_usuario = sistema.adicionar_usuario(nome, senha, is_admin)
                            
                            if novo_usuario:
                                input("\nPressione Enter para continuar...")
                                break
                        elif tipo == "3":
                            break
                        else:
                            print("\nOpção inválida!")
                            input("\nPressione Enter para continuar...")
                else:
                    print("\nErro: É necessário ser um administrador para realizar cadastros.")
                    input("\nPressione Enter para continuar...")

        elif opcao == "3":
            print("\nEncerrando o sistema.")
            break

        else:
            print("Opção inválida. Digite 1, 2 ou 3.")

