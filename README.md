# Inchiesta mobilità — grafici interattivi

Artefatto da pubblicare su **GitHub Pages** ed embeddare su VareseNews. Visualizza
le risposte di un questionario sulla mobilità con un filtro per fascia d'età.

## File

| File | Cosa fa |
|------|---------|
| `index.html` | La pagina con i grafici (autoconsistente, nessuna libreria esterna) |
| `build.py` | Scarica il CSV pubblicato del foglio Google, conta le risposte (COUNT) per colonna e fascia d'età e scrive `data.json` |
| `data.json` | I dati aggregati che alimentano i grafici (generato automaticamente) |
| `.github/workflows/update-data.yml` | Workflow che rigenera `data.json` ogni 3 ore |

## I grafici

- **C** — Esci dal comune? → ciambella (donut) con dato centrale "% esce dal comune"
- **E** — Mezzo più usato → barre orizzontali
- **N** — Problema principale → barre orizzontali
- **G** — Giorni a settimana → colonne verticali
- **H** — Tempo impiegato → colonne verticali
- **I** — Km al giorno → colonne verticali
- **D** — Età → filtro (default "Tutte le fasce d'età"); ricalcola tutti i grafici

Sotto le 15 risposte in una fascia compare un avviso "campione ridotto". Le
percentuali non sommano necessariamente a 100 per via degli arrotondamenti.

## Pubblicazione (una volta sola)

1. Crea un repository **pubblico** su GitHub e carica questi file.
2. Vai in **Settings → Pages** e imposta *Source: Deploy from a branch*, branch
   `main`, cartella `/ (root)`. La pagina sarà su
   `https://<utente>.github.io/<repo>/`.
3. Vai in **Settings → Actions → General → Workflow permissions** e seleziona
   *Read and write permissions* (serve al workflow per committare `data.json`).
4. Apri il tab **Actions**, scegli *Aggiorna dati mobilità* e premi *Run workflow*
   per generare subito il primo `data.json`.

## Aggiornamento automatico

Il workflow gira **ogni 3 ore** (`cron: "0 */3 * * *"`), riscarica il foglio,
ricalcola le percentuali e committa `data.json` solo se qualcosa è cambiato.
È gratuito: GitHub Actions e Pages sono illimitati sui repository pubblici.

> Nota: GitHub sospende i cron sui repo inattivi da 60 giorni; basta un commit
> o un *Run workflow* manuale per riattivarli.

Per cambiare frequenza modifica la riga `cron` (es. `0 */6 * * *` = ogni 6 ore).

## Embed su VareseNews

```html
<iframe id="mobilita" src="https://<utente>.github.io/<repo>/"
        style="width:100%;max-width:600px;border:0" scrolling="no"></iframe>
<script>
  window.addEventListener('message', function (e) {
    if (e.data && e.data['embed-height']) {
      document.getElementById('mobilita').style.height = e.data['embed-height'] + 'px';
    }
  });
</script>
```

La pagina manda al contenitore la propria altezza (`postMessage`) così l'iframe
si adatta senza scrollbar interne. È compatibile anche con *iframe-resizer*.

## Sviluppo locale

```bash
python3 build.py --local   # usa data_raw.csv invece di scaricare
python3 -m http.server 8099
# apri http://localhost:8099
```
