
def get_file_extension(path):
    # Divide il percorso del file in base alla barra "/"
    parts = path.split("/")

    # Ottieni l'ultima parte del percorso, che dovrebbe essere il nome del file
    filename = parts[-1]

    # Dividi il nome del file in base al punto
    name_parts = filename.split(".")

    # Controlla se ci sono più punti nel nome del file
    if len(name_parts) > 2:
        raise ValueError("Invalid filename: more than one dot")

    # Se il nome del file ha un'estensione valida
    if len(name_parts) == 2:
        return name_parts[1]

    # Se il nome del file non ha un'estensione valida
    raise ValueError("Invalid filename: no extension")