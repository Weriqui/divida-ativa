from flask import Flask, request, jsonify
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from unidecode import unidecode

app = Flask(__name__)

# Função para realizar a pesquisa e obter o innerText
def obter_resultado_innerText(valor_pesquisa):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)

    driver.get("https://www.listadevedores.pgfn.gov.br/")

    try:
        input_cnpj = driver.find_element(By.CSS_SELECTOR, '#identificacaoInput')
        input_cnpj.click()
        input_cnpj.send_keys(valor_pesquisa)
        driver.execute_script('document.querySelector("body > dev-root > dev-consulta > main > dev-filtros > div.filtros > div:nth-child(3) > div > button.btn.btn-warning").click()')
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'body > dev-root > dev-consulta > main > dev-resultados > cdk-virtual-scroll-viewport > div.cdk-virtual-scroll-content-wrapper > div > table > tbody > tr > td:nth-child(5) > a > i')))
        driver.execute_script('document.querySelector("body > dev-root > dev-consulta > main > dev-resultados > cdk-virtual-scroll-viewport > div.cdk-virtual-scroll-content-wrapper > div > table > tbody > tr > td:nth-child(5) > a > i").click()')
        time.sleep(3)
        resultado_innerText = driver.execute_script('return document.querySelector("fieldset").innerText')
        lista = resultado_innerText.split('\n')
        resultado = []

        # Percorre a lista de dois em dois elementos
        for i in range(0, len(lista), 2):
            # Verifica se ainda há elementos suficientes para formar um par
            if i + 1 < len(lista):
                tipo = unidecode(lista[i])
                valor = lista[i + 1].split(': ')[1]  # Divide a string pelo ":" e pega o valor depois do ":"
                
                # Cria um dicionário com as informações do tipo e valor e adiciona à lista resultado
                resultado.append({"tipo": tipo, "valor": valor})
        driver.quit()
        return resultado
    except Exception as e:
        # Em caso de erro, feche o navegador e retorne None
        driver.quit()
        return None


@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    # Obtenha o valor de pesquisa enviado no corpo da solicitação POST
    data = request.get_json()
    valor_pesquisa = data['cnpj']
    valor_pesquisa = ''.join([i for i in valor_pesquisa if i.isdigit()])

    # Obtenha o resultado innerText
    resultado = obter_resultado_innerText(valor_pesquisa)

    # Se o resultado não for None, retorne como JSON
    if resultado is not None:
        return jsonify({'resultado_innerText': resultado})
    else:
        return jsonify({'error': 'Erro ao obter o resultado innerText'})

if __name__ == '__main__':
    app.run(debug=True)
