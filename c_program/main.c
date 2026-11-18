/*
 VetCare - módulo complementar em linguagem C.
 Compilar no GCC: gcc main.c -o vetcare
 Executar: ./vetcare (Linux/macOS) ou vetcare.exe (Windows)
 Os registros são salvos em animais.txt durante a execução.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX 300
#define ARQUIVO "animais.txt"

typedef struct {
    int id;
    char nome[80], especie[40], tutor[80];
} Animal;

Animal animais[MAX];
int quantidade = 0;
int proximo_id = 1;

void limpar_buffer(void) {
    int c;
    while ((c = getchar()) != '\n' && c != EOF) {}
}

void ler_texto(const char *rotulo, char *destino, int tamanho) {
    printf("%s", rotulo);
    if (fgets(destino, tamanho, stdin)) {
        destino[strcspn(destino, "\n")] = '\0';
    }
}

void carregar(void) {
    FILE *f = fopen(ARQUIVO, "r");
    if (!f) return;
    while (quantidade < MAX &&
           fscanf(f, "%d|%79[^|]|%39[^|]|%79[^\n]\n",
                  &animais[quantidade].id,
                  animais[quantidade].nome,
                  animais[quantidade].especie,
                  animais[quantidade].tutor) == 4) {
        if (animais[quantidade].id >= proximo_id)
            proximo_id = animais[quantidade].id + 1;
        quantidade++;
    }
    fclose(f);
}

void salvar(void) {
    FILE *f = fopen(ARQUIVO, "w");
    if (!f) {
        printf("Erro ao salvar arquivo.\n");
        return;
    }
    for (int i = 0; i < quantidade; i++) {
        fprintf(f, "%d|%s|%s|%s\n", animais[i].id, animais[i].nome,
                animais[i].especie, animais[i].tutor);
    }
    fclose(f);
}

void cadastrar_animal(void) {
    if (quantidade >= MAX) {
        printf("Limite de animais atingido.\n");
        return;
    }
    Animal a;
    a.id = proximo_id++;
    ler_texto("Nome do animal: ", a.nome, sizeof(a.nome));
    ler_texto("Especie: ", a.especie, sizeof(a.especie));
    ler_texto("Nome do tutor: ", a.tutor, sizeof(a.tutor));
    animais[quantidade++] = a;
    salvar();
    printf("Animal cadastrado! ID: %d\n", a.id);
}

void listar_animais(void) {
    if (!quantidade) {
        printf("Nenhum animal cadastrado.\n");
        return;
    }
    for (int i = 0; i < quantidade; i++)
        printf("ID: %d | Animal: %s | Especie: %s | Tutor: %s\n",
               animais[i].id, animais[i].nome, animais[i].especie,
               animais[i].tutor);
}

void pesquisar_animal(void) {
    char busca[80];
    int encontrou = 0;
    ler_texto("Digite o nome do animal: ", busca, sizeof(busca));
    for (int i = 0; i < quantidade; i++) {
        if (strstr(animais[i].nome, busca) != NULL) {
            printf("ID: %d | %s | %s | Tutor: %s\n", animais[i].id,
                   animais[i].nome, animais[i].especie, animais[i].tutor);
            encontrou = 1;
        }
    }
    if (!encontrou) printf("Animal nao encontrado.\n");
}

void registrar_atendimento(void) {
    char animal[80], descricao[120];
    ler_texto("Nome do animal: ", animal, sizeof(animal));
    ler_texto("Descricao do atendimento: ", descricao, sizeof(descricao));
    FILE *f = fopen("atendimentos.txt", "a");
    if (!f) {
        printf("Nao foi possivel abrir o arquivo.\n");
        return;
    }
    fprintf(f, "Animal: %s | Atendimento: %s\n", animal, descricao);
    fclose(f);
    printf("Atendimento registrado em atendimentos.txt.\n");
}

void registrar_servico(void) {
    char nome[100];
    ler_texto("Nome do servico: ", nome, sizeof(nome));
    FILE *f = fopen("servicos.txt", "a");
    if (!f) {
        printf("Erro ao salvar servico.\n");
        return;
    }
    fprintf(f, "%s\n", nome);
    fclose(f);
    printf("Servico registrado em servicos.txt.\n");
}

void consultar_historico(void) {
    char linha[250];
    FILE *f = fopen("atendimentos.txt", "r");
    if (!f) {
        printf("Ainda nao ha historico.\n");
        return;
    }
    while (fgets(linha, sizeof(linha), f)) printf("%s", linha);
    fclose(f);
}

void relatorio_atendimentos(void) {
    consultar_historico();
}

void faturamento(void) {
    float valor, total = 0;
    int n;
    printf("Quantos valores de atendimento deseja somar? ");
    if (scanf("%d", &n) != 1 || n < 0) {
        limpar_buffer();
        printf("Quantidade invalida.\n");
        return;
    }
    limpar_buffer();
    for (int i = 0; i < n; i++) {
        printf("Valor do atendimento %d (R$): ", i + 1);
        if (scanf("%f", &valor) != 1 || valor < 0) {
            limpar_buffer();
            printf("Valor invalido.\n");
            return;
        }
        total += valor;
    }
    limpar_buffer();
    printf("Faturamento informado: R$ %.2f\n", total);
}

int main(void) {
    int opcao;
    carregar();
    do {
        printf("\n===== VETCARE - CLINICA VETERINARIA =====\n");
        printf("1 - Cadastrar animal\n");
        printf("2 - Listar animais\n");
        printf("3 - Pesquisar animal\n");
        printf("4 - Registrar atendimento\n");
        printf("5 - Registrar servico\n");
        printf("6 - Consultar historico\n");
        printf("7 - Relatorio de atendimentos\n");
        printf("8 - Faturamento\n");
        printf("9 - Sair\n");
        printf("Escolha uma opcao: ");
        if (scanf("%d", &opcao) != 1) {
            limpar_buffer();
            printf("Digite um numero valido.\n");
            continue;
        }
        limpar_buffer();
        switch (opcao) {
            case 1: cadastrar_animal(); break;
            case 2: listar_animais(); break;
            case 3: pesquisar_animal(); break;
            case 4: registrar_atendimento(); break;
            case 5: registrar_servico(); break;
            case 6: consultar_historico(); break;
            case 7: relatorio_atendimentos(); break;
            case 8: faturamento(); break;
            case 9: salvar(); printf("Encerrando o VetCare...\n"); break;
            default: printf("Opcao invalida.\n");
        }
    } while (opcao != 9);
    return 0;
}
