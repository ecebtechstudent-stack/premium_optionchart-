import streamlit as st
import pandas as pd
from datetime import datetime

from nse_data import NSEData
from streamlit_autorefresh import st_autorefresh


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Bank Nifty Derivatives Dashboard",
    page_icon="🏦",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("🏦 Bank Nifty Derivatives Dashboard")
st.subheader("Index + Futures + Options + Stocks")
st.caption("Engineer Ankit")
st.caption("Futures + Options + OI Analysis")


# =========================================================
# NSE OBJECT
# =========================================================

nse = NSEData()


# =========================================================
# BANK NIFTY STOCKS
# =========================================================

BANK_STOCKS = [
    "AUBANK",
    "AXISBANK",
    "BANKBARODA",
    "CANBK",
    "FEDERALBNK",
    "HDFCBANK",
    "ICICIBANK",
    "IDFCFIRSTB",
    "INDUSINDBK",
    "KOTAKBANK",
    "PNB",
    "SBIN"
]


# =========================================================
# SESSION STATE
# =========================================================

if "auto_loaded" not in st.session_state:
    st.session_state.auto_loaded = False

if "last_updated" not in st.session_state:
    st.session_state.last_updated = None


# =========================================================
# OI ANALYSIS FUNCTION
# =========================================================

def oi_analysis(price_change, oi_change):

    try:

        price_change = float(price_change)
        oi_change = float(oi_change)

    except Exception:

        return "N/A"

    if price_change > 0 and oi_change > 0:

        return "🟢 Long Buildup"

    elif price_change < 0 and oi_change > 0:

        return "🔴 Short Buildup"

    elif price_change > 0 and oi_change < 0:

        return "🟡 Short Covering"

    elif price_change < 0 and oi_change < 0:

        return "🔵 Long Unwinding"

    else:

        return "⚪ Neutral"


# =========================================================
# GET RECORDS
# =========================================================

def get_records(raw_data):

    if isinstance(raw_data, dict):

        if isinstance(raw_data.get("data"), list):

            return raw_data["data"]

        elif isinstance(raw_data.get("data"), dict):

            return [raw_data["data"]]

        else:

            return [raw_data]

    elif isinstance(raw_data, list):

        return raw_data

    return []


# =========================================================
# OVERALL STOCK ANALYSIS
# =========================================================

def overall_stock_analysis(stock, raw_data):

    result = {

        "Stock": stock,

        "🟢 Long Buildup": 0,

        "🔴 Short Buildup": 0,

        "🟡 Short Covering": 0,

        "🔵 Long Unwinding": 0,

        "⚪ Neutral": 0
    }

    try:

        records = get_records(raw_data)

        if not records:

            return result

        stock_df = pd.DataFrame(records)

        if (
            "pchange" not in stock_df.columns
            or
            "changeinOpenInterest" not in stock_df.columns
        ):

            return result

        stock_df["pchange"] = pd.to_numeric(
            stock_df["pchange"],
            errors="coerce"
        )

        stock_df["changeinOpenInterest"] = pd.to_numeric(
            stock_df["changeinOpenInterest"],
            errors="coerce"
        )

        for _, row in stock_df.iterrows():

            signal = oi_analysis(
                row["pchange"],
                row["changeinOpenInterest"]
            )

            if signal in result:

                result[signal] += 1

    except Exception:

        pass

    return result


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Dashboard Settings")


symbol = st.sidebar.selectbox(
    "Select Stock",
    BANK_STOCKS
)


# =========================================================
# TIMEFRAME / AUTO REFRESH
# =========================================================

refresh_time = st.sidebar.selectbox(

    "⏱️ Timeframe / Auto Refresh",

    [
        "1 Minute",
        "5 Minutes",
        "15 Minutes",
        "30 Minutes",
        "1 Hour",
        "4 Hours",
        "1 Day"
    ],

    index=1
)


# =========================================================
# REFRESH SECONDS
# =========================================================

refresh_seconds = {

    "1 Minute": 60,

    "5 Minutes": 300,

    "15 Minutes": 900,

    "30 Minutes": 1800,

    "1 Hour": 3600,

    "4 Hours": 14400,

    "1 Day": 86400

}[refresh_time]


# =========================================================
# LOAD BUTTON
# =========================================================

load_data = st.sidebar.button(

    "🚀 Load / Refresh Data",

    use_container_width=True
)


if load_data:

    st.session_state.auto_loaded = True


# =========================================================
# AUTO REFRESH
# =========================================================

if st.session_state.auto_loaded:

    st_autorefresh(

        interval=refresh_seconds * 1000,

        key="dashboard_auto_refresh"
    )

    st.sidebar.success(

        f"🔄 Auto update: Every {refresh_time}"
    )

else:

    st.sidebar.info(

        "⏱️ Click Load / Refresh Data"
    )


# =========================================================
# LAST UPDATED
# =========================================================

if st.session_state.last_updated:

    st.sidebar.caption(

        "🕐 Last Updated: "
        + st.session_state.last_updated
    )


# =========================================================
# MAIN DASHBOARD
# =========================================================

if st.session_state.auto_loaded:

    with st.spinner(
        "⏳ Loading NSE derivative data..."
    ):

        try:

            # =================================================
            # SELECTED STOCK DATA
            # =================================================

            data = nse.derivative_quote(
                symbol
            )


            records = get_records(
                data
            )


            if not records:

                st.warning(
                    "⚠️ No derivative data found."
                )

                st.stop()


            df = pd.DataFrame(
                records
            )


            # =================================================
            # NUMERIC COLUMNS
            # =================================================

            numeric_columns = [

                "lastPrice",

                "openInterest",

                "changeinOpenInterest",

                "pchange",

                "strikePrice"

            ]


            for col in numeric_columns:

                if col in df.columns:

                    df[col] = pd.to_numeric(

                        df[col],

                        errors="coerce"
                    )


            # =================================================
            # OPTION TYPE
            # =================================================

            if "optionType" in df.columns:

                df["optionType"] = (

                    df["optionType"]
                    .astype(str)
                    .str.upper()

                )


            # =================================================
            # CE DATA
            # =================================================

            ce = pd.DataFrame()


            if "optionType" in df.columns:

                ce = df[
                    df["optionType"] == "CE"
                ].copy()


            ce = ce.rename(

                columns={

                    "lastPrice":
                        "CE LTP",

                    "openInterest":
                        "CE OI",

                    "changeinOpenInterest":
                        "CE OI Change",

                    "pchange":
                        "CE Price Change %"

                }
            )


            # =================================================
            # PE DATA
            # =================================================

            pe = pd.DataFrame()


            if "optionType" in df.columns:

                pe = df[
                    df["optionType"] == "PE"
                ].copy()


            pe = pe.rename(

                columns={

                    "lastPrice":
                        "PE LTP",

                    "openInterest":
                        "PE OI",

                    "changeinOpenInterest":
                        "PE OI Change",

                    "pchange":
                        "PE Price Change %"

                }
            )


            # =================================================
            # MERGE CE + PE
            # =================================================

            if (
                not ce.empty
                and
                not pe.empty
            ):

                df_final = pd.merge(

                    ce[
                        [
                            "strikePrice",
                            "CE LTP",
                            "CE OI",
                            "CE OI Change",
                            "CE Price Change %"
                        ]
                    ],

                    pe[
                        [
                            "strikePrice",
                            "PE LTP",
                            "PE OI",
                            "PE OI Change",
                            "PE Price Change %"
                        ]
                    ],

                    on="strikePrice",

                    how="outer"
                )


            elif not ce.empty:

                df_final = ce


            elif not pe.empty:

                df_final = pe


            else:

                df_final = pd.DataFrame()


            # =================================================
            # SORT
            # =================================================

            if not df_final.empty:

                if "strikePrice" in df_final.columns:

                    df_final = df_final.sort_values(
                        by="strikePrice"
                    )


            # =================================================
            # CE OI ANALYSIS
            # =================================================

            if (
                "CE Price Change %" in df_final.columns
                and
                "CE OI Change" in df_final.columns
            ):

                df_final["CE OI Analysis"] = (

                    df_final.apply(

                        lambda row:

                        oi_analysis(

                            row[
                                "CE Price Change %"
                            ],

                            row[
                                "CE OI Change"
                            ]

                        ),

                        axis=1
                    )
                )


            # =================================================
            # PE OI ANALYSIS
            # =================================================

            if (
                "PE Price Change %" in df_final.columns
                and
                "PE OI Change" in df_final.columns
            ):

                df_final["PE OI Analysis"] = (

                    df_final.apply(

                        lambda row:

                        oi_analysis(

                            row[
                                "PE Price Change %"
                            ],

                            row[
                                "PE OI Change"
                            ]

                        ),

                        axis=1
                    )
                )


            # =================================================
            # RENAME STRIKE
            # =================================================

            if "strikePrice" in df_final.columns:

                df_final = df_final.rename(

                    columns={

                        "strikePrice":
                            "Strike Price"

                    }
                )


            # =================================================
            # LAST UPDATED
            # =================================================

            current_time = datetime.now().strftime(

                "%d-%m-%Y %I:%M:%S %p"

            )


            st.session_state.last_updated = (

                current_time
            )


            # =================================================
            # BANKNIFTY INDEX
            # =================================================

            st.markdown(
                "## 🏦 BANKNIFTY INDEX"
            )

            st.info(

                "BANKNIFTY Index data will be displayed here when the NSE response provides the index quote."
            )


            # =================================================
            # BANKNIFTY FUTURES
            # =================================================

            st.markdown(
                "## 📈 BANKNIFTY FUTURES"
            )

            st.info(

                "BANKNIFTY Futures data will be displayed here when the NSE response provides the futures instrument data."
            )


            # =================================================
            # BANKNIFTY OPTIONS
            # =================================================

            st.markdown(
                "## 📊 OPTIONS DATA"
            )

            st.caption(

                f"Selected Stock: {symbol}"
            )


            # =================================================
            # ALL BANK NIFTY STOCKS
            # =================================================

            st.markdown(

                "## 🏢 ALL BANK NIFTY DERIVATIVE STOCKS"

            )


            st.caption(

                "CE + PE combined OI classification"

            )


            overall_rows = []


            for stock in BANK_STOCKS:

                try:

                    if stock == symbol:

                        stock_data = data

                    else:

                        stock_data = nse.derivative_quote(
                            stock
                        )


                    row = overall_stock_analysis(

                        stock,

                        stock_data
                    )


                    overall_rows.append(
                        row
                    )


                except Exception:

                    overall_rows.append({

                        "Stock":
                            stock,

                        "🟢 Long Buildup":
                            0,

                        "🔴 Short Buildup":
                            0,

                        "🟡 Short Covering":
                            0,

                        "🔵 Long Unwinding":
                            0,

                        "⚪ Neutral":
                            0
                    })


            overall_df = pd.DataFrame(

                overall_rows
            )


            # =================================================
            # TOTAL ROW
            # =================================================

            total_row = {

                "Stock":
                    "TOTAL",

                "🟢 Long Buildup":
                    overall_df[
                        "🟢 Long Buildup"
                    ].sum(),

                "🔴 Short Buildup":
                    overall_df[
                        "🔴 Short Buildup"
                    ].sum(),

                "🟡 Short Covering":
                    overall_df[
                        "🟡 Short Covering"
                    ].sum(),

                "🔵 Long Unwinding":
                    overall_df[
                        "🔵 Long Unwinding"
                    ].sum(),

                "⚪ Neutral":
                    overall_df[
                        "⚪ Neutral"
                    ].sum()

            }


            overall_df = pd.concat(

                [

                    overall_df,

                    pd.DataFrame(
                        [total_row]
                    )

                ],

                ignore_index=True

            )


            st.dataframe(

                overall_df,

                use_container_width=True,

                hide_index=True

            )


            # =================================================
            # MARKET OVERVIEW
            # =================================================

            if not df_final.empty:

                st.markdown(

                    f"## 📊 {symbol} Market Overview"

                )


                total_ce_oi = pd.to_numeric(

                    df_final.get(

                        "CE OI",

                        pd.Series(
                            dtype=float
                        )

                    ),

                    errors="coerce"

                ).fillna(0).sum()


                total_pe_oi = pd.to_numeric(

                    df_final.get(

                        "PE OI",

                        pd.Series(
                            dtype=float
                        )

                    ),

                    errors="coerce"

                ).fillna(0).sum()


                ce_premium = pd.to_numeric(

                    df_final.get(

                        "CE LTP",

                        pd.Series(
                            dtype=float
                        )

                    ),

                    errors="coerce"

                ).fillna(0).sum()


                pe_premium = pd.to_numeric(

                    df_final.get(

                        "PE LTP",

                        pd.Series(
                            dtype=float
                        )

                    ),

                    errors="coerce"

                ).fillna(0).sum()


                pcr = (

                    total_pe_oi /
                    total_ce_oi

                    if total_ce_oi != 0

                    else 0

                )


                # =================================================
                # METRICS
                # =================================================

                c1, c2, c3, c4 = st.columns(4)


                with c1:

                    st.metric(

                        "📈 Total CE OI",

                        f"{total_ce_oi:,.0f}"

                    )


                with c2:

                    st.metric(

                        "📉 Total PE OI",

                        f"{total_pe_oi:,.0f}"

                    )


                with c3:

                    st.metric(

                        "⚖️ PCR",

                        f"{pcr:.2f}"

                    )


                with c4:

                    st.metric(

                        "💰 CE + PE Premium",

                        f"{ce_premium + pe_premium:,.2f}"

                    )


                # =================================================
                # PREMIUM OVERVIEW
                # =================================================

                st.markdown(

                    "## 💰 Premium Overview"

                )


                c1, c2, c3 = st.columns(3)


                with c1:

                    st.metric(

                        "CE Premium",

                        f"{ce_premium:,.2f}"

                    )


                with c2:

                    st.metric(

                        "PE Premium",

                        f"{pe_premium:,.2f}"

                    )


                with c3:

                    st.metric(

                        "Premium Difference",

                        f"{ce_premium - pe_premium:,.2f}"

                    )


                # =================================================
                # OI ANALYSIS
                # =================================================

                st.markdown(

                    "## 🔄 OI Analysis"

                )


                c1, c2 = st.columns(2)


                with c1:

                    st.markdown(

                        "### 📈 Call Side Analysis"

                    )


                    if "CE OI Analysis" in df_final.columns:

                        ce_counts = (

                            df_final[
                                "CE OI Analysis"
                            ]
                            .value_counts()
                        )


                        for name, value in ce_counts.items():

                            st.write(

                                f"**{name}:** {value}"

                            )


                with c2:

                    st.markdown(

                        "### 📉 Put Side Analysis"

                    )


                    if "PE OI Analysis" in df_final.columns:

                        pe_counts = (

                            df_final[
                                "PE OI Analysis"
                            ]
                            .value_counts()
                        )


                        for name, value in pe_counts.items():

                            st.write(

                                f"**{name}:** {value}"

                            )


                # =================================================
                # COMPLETE OPTIONS CHAIN
                # =================================================

                st.markdown(

                    "## 📋 Complete Options Chain"

                )


                st.dataframe(

                    df_final,

                    use_container_width=True,

                    hide_index=True,

                    height=600

                )


                # =================================================
                # POSITION ANALYSIS
                # =================================================

                st.markdown(

                    "## 🎯 Position Analysis"

                )


                ce_analysis = (

                    df_final.get(

                        "CE OI Analysis",

                        pd.Series(
                            dtype=str
                        )

                    )
                    .astype(str)

                )


                pe_analysis = (

                    df_final.get(

                        "PE OI Analysis",

                        pd.Series(
                            dtype=str
                        )

                    )
                    .astype(str)

                )


                c1, c2, c3, c4 = st.columns(4)


                with c1:

                    st.metric(

                        "🟢 CE Long Buildup",

                        ce_analysis.str.contains(

                            "Long Buildup"

                        ).sum()

                    )


                with c2:

                    st.metric(

                        "🔴 CE Short Buildup",

                        ce_analysis.str.contains(

                            "Short Buildup"

                        ).sum()

                    )


                with c3:

                    st.metric(

                        "🟢 PE Long Buildup",

                        pe_analysis.str.contains(

                            "Long Buildup"

                        ).sum()

                    )


                with c4:

                    st.metric(

                        "🔴 PE Short Buildup",

                        pe_analysis.str.contains(

                            "Short Buildup"

                        ).sum()

                    )


            # =================================================
            # MARKET INFORMATION
            # =================================================

            st.markdown(

                "## 🧠 Market Information"

            )


            c1, c2 = st.columns(2)


            with c1:

                st.info(

                    f"""
**Selected Stock:** {symbol}

**Timeframe / Refresh:** {refresh_time}

**Last Updated:** {current_time}

**PCR:** {pcr:.2f}

**CE OI:** {total_ce_oi:,.0f}

**PE OI:** {total_pe_oi:,.0f}

**CE Premium:** {ce_premium:,.2f}

**PE Premium:** {pe_premium:,.2f}
"""

                )


            with c2:

                if pcr > 1:

                    st.info(
                        "PE OI is higher than CE OI."
                    )

                elif pcr < 1:

                    st.info(
                        "CE OI is higher than PE OI."
                    )

                else:

                    st.info(
                        "CE OI and PE OI are approximately equal."
                    )


        except Exception as e:

            st.error(

                f"❌ Data load error: {e}"

            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(

    "OI Analysis = Price Change + Open Interest Change."

)

st.caption(

    "Timeframe controls how frequently the dashboard requests a new snapshot."

)