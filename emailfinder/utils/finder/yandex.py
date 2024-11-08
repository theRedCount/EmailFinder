import requests
import urllib3
from time import sleep
from random import randint, uniform
from emailfinder.utils.exception import YandexDetection
from emailfinder.utils.agent import user_agent
from emailfinder.utils.file.email_parser import get_emails
from emailfinder.utils.color_print import print_info, print_ok

urllib3.disable_warnings()

def search(target, total=50, proxies=None):
    old_text = ""
    num_results = 50 if total >= 50 else total
    emails = set()
    base_url = "https://www.yandex.ru/search/?"
    total_loop = int(total / num_results)
    if (total % num_results) != 0:
        total_loop += 1
    count = 1
    old_useragent = -1
    total_timeout = 0

    while count <= total_loop:
        # Seleziona un nuovo user-agent, evitando di riutilizzare l'ultimo
        while True:
            next_useragent = randint(0, len(user_agent) - 1)
            if next_useragent != old_useragent:
                break
        old_useragent = next_useragent
        headers = user_agent.get(next_useragent)

        # Costruisce l'URL della richiesta
        new_url = base_url + f'text=%40{target}&numdoc={num_results}&p={count - 1}&lr=10435'
        try:
            response = requests.get(
                new_url,
                headers=headers,
                timeout=5,
                verify=False,
                proxies=proxies
            )
            text = response.text

            # Rilevamento bot: pausa e ritenta
            if "robot are sending requests" in text:
                total_timeout += 1
                print_info("Yandex detected bot activity. Pausing and retrying...")
                if total_timeout >= 3:
                    raise YandexDetection("Yandex bot detection triggered multiple times.")
                sleep(10 + uniform(5, 10))  # Pausa di 10-20 secondi per ridurre il rischio
                continue

            # Se il contenuto è duplicato rispetto alla richiesta precedente, interrompe il ciclo
            if old_text == text:
                print_info("Duplicate content detected. Stopping further requests.")
                break
            old_text = text

            # Estrai e aggiungi le email uniche al set
            emails.update(get_emails(target, text))

            # Pausa casuale tra le richieste per evitare il rilevamento
            sleep(uniform(5, 10))
            count += 1  # Incrementa il contatore per passare alla pagina successiva

        except YandexDetection as e:
            print_info(str(e))
            break  # Esce dal ciclo se viene rilevato come bot

        except Exception as ex:
            print_info(f"Error during Yandex search: {ex}")
            break  # Interrompe la ricerca in caso di altri errori

    emails = list(emails)
    if emails:
        print_ok(f"Yandex discovered {len(emails)} unique emails")
    else:
        print_info("Yandex did not discover any email IDs")
    return emails
