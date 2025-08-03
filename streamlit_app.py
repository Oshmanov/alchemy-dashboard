import os, requests, streamlit as st, pandas as pd

ALCHEMY = os.getenv("ALCHEMY_URL")  # берётся из secrets.toml
HEADERS = {"accept": "application/json", "content-type": "application/json"}

st.title("Ethereum Address Explorer (Alchemy API)")

addr = st.text_input("Введите адрес или ENS", "vitalik.eth")
if st.button("Fetch"):
    # --- 1. Баланс ETH ---
    payload = {"jsonrpc":"2.0","id":1,"method":"alchemy_getBalance",
               "params":[addr,"latest"]}
    bal_raw = requests.post(ALCHEMY, json=payload, headers=HEADERS).json()
    eth = int(bal_raw["result"], 16) / 10**18
    st.metric("Баланс ETH", f"{eth:,.4f} ETH")

    # --- 2. Токены (top-10) ---
    payload = {"jsonrpc":"2.0","id":1,"method":"alchemy_getTokenBalances",
               "params":[addr, "erc20"]}
    tok = requests.post(ALCHEMY, json=payload, headers=HEADERS).json()
    rows = []
    for t in tok["result"]["tokenBalances"]:
        if t["tokenBalance"] == "0x": continue
        bal = int(t["tokenBalance"],16)
        rows.append({"token": t["contractAddress"], "raw": bal})
    df = pd.DataFrame(rows).sort_values("raw", ascending=False)[:10]
    st.subheader("Топ-10 токенов")
    st.dataframe(df, use_container_width=True)

    # --- 3. Последние 20 трансферов ---
    payload = {
      "jsonrpc":"2.0","id":1,"method":"alchemy_getAssetTransfers",
      "params":[{"fromBlock":"0x0","toAddress":addr,"category":["external","erc20","erc721"],
                 "maxCount":"0x14"}] }  # 0x14 = 20
    txs = requests.post(ALCHEMY, json=payload, headers=HEADERS).json()
    tdf = pd.json_normalize(txs["result"])
    st.subheader("Последние 20 транзакций")
    st.dataframe(tdf[["hash","value","asset","blockNum"]], use_container_width=True)
