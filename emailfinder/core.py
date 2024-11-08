import logging
from emailfinder.utils.finder import google, bing, baidu, yandex, duckduckgo, ask, reddit
from emailfinder.utils.color_print import print_error, print_ok
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurazione di logging
logging.basicConfig(level=logging.INFO, filename='emailfinder.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Dizionario dei metodi dei motori di ricerca
SEARCH_ENGINES_METHODS = {
    "google": google.search,
    # "bing": bing.search,
    # "baidu": baidu.search,
    # "yandex": yandex.search,
    # "duckduckgo": duckduckgo.search,
    # "ask": ask.search,
    # "reddit": reddit.search,
}

# Timeout per ogni ricerca in secondi
SEARCH_TIMEOUT = 10

def _search(engine, target, proxy_dict):
    """
    Funzione di supporto per eseguire la ricerca su un motore specifico.
    """
    emails = set()  # Inizializza un set per ogni motore di ricerca
    logging.info(f"Starting search on {engine} for target: {target}")
    try:
        # Verifica se la funzione di ricerca supporta il parametro `timeout`
        search_function = SEARCH_ENGINES_METHODS[engine]
        search_params = {"target": target, "proxies": proxy_dict}
        if "timeout" in search_function.__code__.co_varnames:
            search_params["timeout"] = SEARCH_TIMEOUT

        emails = search_function(**search_params)
        print_ok(f"{engine} search completed successfully!")
        logging.info(f"{engine} search completed successfully!")
    except Exception as ex:
        print_error(f"{engine} encountered an error: {ex}")
        logging.error(f"{engine} encountered an error: {ex}")
    return emails

def _get_emails(target, proxy_dict):
    """
    Esegue le ricerche su tutti i motori di ricerca in parallelo e aggrega i risultati.
    """
    emails = set()  # Usa un set per aggregare i risultati senza duplicati
    threads = min(4, len(SEARCH_ENGINES_METHODS))  # Usa solo i thread necessari per i motori attivi
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_emails = {executor.submit(_search, engine, target, proxy_dict): engine for engine in SEARCH_ENGINES_METHODS.keys()}
        for future in as_completed(future_emails):
            engine = future_emails[future]
            try:
                data = future.result()
                if data:
                    emails.update(data)  # Aggiorna il set con i risultati senza duplicati
            except Exception as ex:
                print_error(f"Error in {engine}: {ex}")
                logging.error(f"Error in {engine}: {ex}")
    return list(emails)  # Converte il set in una lista per il ritorno finale

def processing(target, proxies):
    """
    Gestisce l'intero processo di ricerca per un target specifico, utilizzando proxy se specificato.
    """
    proxy_dict = None
    if proxies:
        print("Using proxies")
        proxy_dict = {
            "http": proxies,
            "https": proxies
        }

    emails = _get_emails(target, proxy_dict=proxy_dict)
    total_emails = len(emails)
    emails_msg = f"\nTotal unique emails found: {total_emails}"
    print(emails_msg)
    print("-" * len(emails_msg))
    logging.info(emails_msg)
    
    if total_emails > 0:
        for email in emails:
            print(email)
            logging.info(f"Found email: {email}")
    else:
        print("0 emails found. Closing...")
        logging.info("0 emails found. Closing...")
