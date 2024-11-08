import requests
from random import randint, uniform
import time
from bs4 import BeautifulSoup
from emailfinder.utils.exception import GoogleCaptcha, GoogleCookiePolicies
from emailfinder.utils.agent import user_agent
from emailfinder.utils.file.email_parser import get_emails
from emailfinder.utils.color_print import print_info, print_ok

def search(target, proxies=None, total=200):
    emails = set()
    start = 0
    num = 50 if total > 50 else total
    iterations = int(total / num)
    if (total % num) != 0:
        iterations += 1
    url_base = f"https://www.google.com/search?q=intext:@{target}&num={num}"
    cookies = {"CONSENT": "YES+srp.gws"}  # Consenso ai cookie
    session = requests.Session()  # Usa una sessione per mantenere i cookie
    
    while start < iterations:
        try:
            url = url_base + f"&start={start * num}"
            headers = user_agent.get(randint(0, len(user_agent) - 1))
            response = session.get(url, headers=headers, cookies=cookies, verify=False, proxies=proxies)

            # Verifica se Google sta bloccando la richiesta con una pagina di consenso o captcha
            text = response.text
            if response.status_code == 302 and ("https://www.google.com/webhp" in text or "https://consent.google.com" in text):
                raise GoogleCookiePolicies("Cookie consent page detected.")
            elif "detected unusual traffic" in text or "sorry" in text.lower():
                raise GoogleCaptcha("Captcha detected. Google suspects unusual traffic.")

            # Verifica e pulizia del testo HTML prima del parsing
            if not text.strip().startswith("<!DOCTYPE html>") and not "<html" in text:
                print_info("Google returned non-HTML content. Skipping parsing.")
                break

            # Estrazione delle email dalla pagina
            emails.update(get_emails(target, text))
            soup = BeautifulSoup(text, "html.parser")
            # Se il numero di risultati è inferiore a `num`, non ci sono altre pagine
            if len(soup.find_all("h3")) < num:
                break

            # Attendi un tempo casuale tra 1 e 3 secondi per simulare il comportamento umano
            time.sleep(uniform(1, 3))
        
        except GoogleCookiePolicies as e:
            print_info(str(e))
            break  # Esce dal ciclo se viene rilevata la pagina di consenso ai cookie
        
        except GoogleCaptcha as e:
            print_info(str(e))
            break  # Esce dal ciclo se viene rilevato il captcha
        
        except Exception as ex:
            print_info(f"Error during Google search: {ex}")
            break  # Interrompe la ricerca in caso di altri errori

        start += 1

    emails = list(emails)
    if emails:
        print_ok(f"Google discovered {len(emails)} emails")
    else:
        print_info("Google did not discover any email IDs")
    return emails
