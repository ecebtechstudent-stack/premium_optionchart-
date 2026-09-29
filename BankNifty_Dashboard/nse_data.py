import json
import os
import requests
from datetime import datetime


class NSEData:

    def __init__(self):

        self.session = requests.Session()

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/146.0.0.0 Safari/537.36"
            ),

            "Accept-Language": "en-IN,en;q=0.9",

            "Referer":
                "https://www.nseindia.com/",

            "Connection":
                "keep-alive",
        }

        self.session.headers.update(
            self.headers
        )

        self.refresh_session()


    # =====================================================
    # SESSION REFRESH
    # =====================================================

    def refresh_session(self, symbol="AUBANK"):

        try:

            self.session.get(
                "https://www.nseindia.com/",
                timeout=15
            )

            self.session.get(
                "https://www.nseindia.com/market-data/live-equity-market",
                timeout=15
            )

            self.session.get(
                "https://www.nseindia.com/get-quotes/equity"
                f"?symbol={symbol}",
                timeout=15
            )

        except requests.RequestException:

            pass


    # =====================================================
    # DERIVATIVE DATA
    # =====================================================

    def derivative_quote(self, symbol):

        symbol = symbol.upper().strip()

        url = (
            "https://www.nseindia.com/api/NextApi/apiClient/"
            "GetQuoteApi"
        )

        params = {
            "functionName":
                "getSymbolDerivativesData",

            "symbol":
                symbol,
        }

        headers = {

            "User-Agent":
                self.headers["User-Agent"],

            "Accept":
                "application/json, text/plain, */*",

            "Accept-Language":
                "en-IN,en;q=0.9",

            "Referer":
                (
                    "https://www.nseindia.com/"
                    "get-quotes/equity"
                    f"?symbol={symbol}"
                ),

            "X-Requested-With":
                "XMLHttpRequest",
        }


        response = self.session.get(

            url,

            params=params,

            headers=headers,

            timeout=15
        )


        # -------------------------------------------------
        # 403 RETRY
        # -------------------------------------------------

        if response.status_code == 403:

            self.refresh_session(
                symbol
            )

            response = self.session.get(

                url,

                params=params,

                headers=headers,

                timeout=15
            )


        response.raise_for_status()


        return response.json()


    # =====================================================
    # BANKNIFTY DERIVATIVE DATA
    # =====================================================

    def banknifty_derivatives(self):

        return self.derivative_quote(
            "BANKNIFTY"
        )


    # =====================================================
    # SAVE SNAPSHOT
    # =====================================================

    def save_snapshot(
        self,
        symbol,
        data
    ):

        folder = "snapshots"

        os.makedirs(
            folder,
            exist_ok=True
        )

        filename = os.path.join(

            folder,

            f"{symbol}_snapshots.json"
        )


        snapshot = {

            "timestamp":
                datetime.now().isoformat(),

            "symbol":
                symbol,

            "data":
                data
        }


        snapshots = []


        if os.path.exists(filename):

            try:

                with open(

                    filename,

                    "r",

                    encoding="utf-8"

                ) as file:

                    snapshots = json.load(
                        file
                    )

            except Exception:

                snapshots = []


        if not isinstance(
            snapshots,
            list
        ):

            snapshots = []


        snapshots.append(
            snapshot
        )


        # Last 500 snapshots
        snapshots = snapshots[-500:]


        with open(

            filename,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                snapshots,

                file,

                indent=2,

                ensure_ascii=False,

                default=str
            )


    # =====================================================
    # GET SNAPSHOTS
    # =====================================================

    def get_snapshots(
        self,
        symbol
    ):

        filename = os.path.join(

            "snapshots",

            f"{symbol}_snapshots.json"
        )


        if not os.path.exists(
            filename
        ):

            return []


        try:

            with open(

                filename,

                "r",

                encoding="utf-8"

            ) as file:

                snapshots = json.load(
                    file
                )


            if isinstance(
                snapshots,
                list
            ):

                return snapshots


        except Exception:

            pass


        return []