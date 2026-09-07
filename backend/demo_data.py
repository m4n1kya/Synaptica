"""
Synaptica — Pre-computed Demo Data
Realistic fact extractions from the India Macroeconomy and Delhivery starter datasets.
This ensures the demo works instantly without requiring an LLM API key.
"""
from models import Fact, Relationship, Document, Context, CaseStudy


def get_demo_documents():
    """Return pre-configured document metadata for all 6 starter PDFs."""
    return [
        Document(
            id="doc-eco-survey",
            filename="01-india-economic-survey-2024-25-excerpt.pdf",
            original_filename="Economic Survey 2024-25",
            page_count=89,
            fact_count=0,  # Will be updated after facts are loaded
            status="processed",
            dataset="india-macroeconomy",
            description="Government of India Economic Survey for FY2024-25, covering state of the economy, external sector, prices and inflation."
        ),
        Document(
            id="doc-rbi-annual",
            filename="02-rbi-annual-report-2024-25-excerpt.pdf",
            original_filename="RBI Annual Report 2024-25",
            page_count=100,
            fact_count=0,
            status="processed",
            dataset="india-macroeconomy",
            description="Reserve Bank of India Annual Report covering economic assessment, macroeconomic review, and statistical appendix tables."
        ),
        Document(
            id="doc-imf-article",
            filename="03-imf-india-2025-article-iv-excerpt.pdf",
            original_filename="IMF India Article IV 2025",
            page_count=95,
            fact_count=0,
            status="processed",
            dataset="india-macroeconomy",
            description="IMF Article IV Consultation staff report with statistical tables and annexes on India's economic outlook."
        ),
        Document(
            id="doc-delhivery-prospectus",
            filename="01-delhivery-prospectus-2022-excerpt.pdf",
            original_filename="Delhivery Prospectus 2022",
            page_count=100,
            fact_count=0,
            status="processed",
            dataset="delhivery",
            description="IPO prospectus with corporate summary, financial statements, business overview, and management details."
        ),
        Document(
            id="doc-delhivery-annual",
            filename="02-delhivery-annual-report-fy24-excerpt.pdf",
            original_filename="Delhivery Annual Report FY24",
            page_count=100,
            fact_count=0,
            status="processed",
            dataset="delhivery",
            description="Annual report with directors' report, MD&A, corporate governance, and consolidated financials."
        ),
        Document(
            id="doc-delhivery-q4",
            filename="03-delhivery-q4-fy24-earnings-presentation.pdf",
            original_filename="Delhivery Q4 FY24 Earnings",
            page_count=27,
            fact_count=0,
            status="processed",
            dataset="delhivery",
            description="Q4 FY24 earnings presentation with quarterly financials and operational metrics."
        ),
    ]


def get_demo_facts():
    """Return comprehensive, realistic facts extracted from the starter datasets."""
    facts = []

    # ========================================================================
    # INDIA MACROECONOMY — Economic Survey 2024-25
    # ========================================================================
    eco_survey_facts = [
        Fact(
            id="eco-gdp-growth-01",
            statement="India's real GDP growth for FY2024-25 is estimated at 6.5 per cent",
            value="6.5", unit="%", category="GDP Growth", confidence=0.96,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[46, 47],
            evidence_text="India's real GDP is estimated to grow at 6.5 per cent in 2024-25, supported by robust domestic consumption and a recovery in private capital expenditure.",
            context=Context(time_period="FY2024-25", scope="India (National)", methodology="Advance Estimate, CSO")
        ),
        Fact(
            id="eco-gdp-nominal-02",
            statement="Nominal GDP for FY2024-25 is estimated at ₹326.37 lakh crore",
            value="326.37", unit="₹ Lakh Crore", category="GDP Growth", confidence=0.97,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[48],
            evidence_text="The nominal GDP for 2024-25 is estimated at ₹326.37 lakh crore (US$ 3.89 trillion at current exchange rates).",
            context=Context(time_period="FY2024-25", scope="India (National)", methodology="Advance Estimate")
        ),
        Fact(
            id="eco-cpi-inflation-03",
            statement="Average CPI inflation for FY2024-25 moderated to 4.9 per cent",
            value="4.9", unit="%", category="Inflation", confidence=0.95,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[124, 125],
            evidence_text="Headline CPI inflation averaged 4.9 per cent during April-December 2024, moderating from 5.4 per cent in the corresponding period of the previous year, driven by a decline in core inflation.",
            context=Context(time_period="Apr-Dec FY2024-25", scope="India (National)", methodology="CPI-Combined, NSO")
        ),
        Fact(
            id="eco-food-inflation-04",
            statement="Food inflation remained elevated at 7.6 per cent in H1 FY2024-25",
            value="7.6", unit="%", category="Inflation", confidence=0.93,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[130],
            evidence_text="Food inflation, which has a weight of 39.06 per cent in the CPI basket, averaged 7.6 per cent during H1:2024-25, primarily driven by vegetables, pulses, and cereals.",
            context=Context(time_period="H1 FY2024-25 (Apr-Sep 2024)", scope="India (National)", methodology="CPI-Food, NSO")
        ),
        Fact(
            id="eco-core-inflation-05",
            statement="Core inflation (excluding food and fuel) fell to a historic low of 3.1 per cent",
            value="3.1", unit="%", category="Inflation", confidence=0.94,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[126],
            evidence_text="Core CPI inflation (excluding food and fuel) has fallen to a historic low, averaging 3.1 per cent during April-December 2024-25.",
            context=Context(time_period="Apr-Dec FY2024-25", scope="India (National)", methodology="CPI excluding food & fuel")
        ),
        Fact(
            id="eco-fiscal-deficit-06",
            statement="Fiscal deficit for FY2024-25 is estimated at 4.9 per cent of GDP (Revised Estimate)",
            value="4.9", unit="% of GDP", category="Fiscal Policy", confidence=0.97,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[52],
            evidence_text="The revised estimate for the fiscal deficit in FY2024-25 stands at 4.9 per cent of GDP, lower than the budget estimate of 5.1 per cent, reflecting buoyant tax revenue collections.",
            context=Context(time_period="FY2024-25", scope="Central Government", methodology="Revised Estimates (RE)")
        ),
        Fact(
            id="eco-cad-07",
            statement="Current account deficit narrowed to 1.2 per cent of GDP in H1 FY2024-25",
            value="1.2", unit="% of GDP", category="External Sector", confidence=0.95,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[72, 73],
            evidence_text="India's current account deficit (CAD) narrowed to 1.2 per cent of GDP in H1:2024-25, compared to 1.0 per cent in H1:2023-24, owing to a widening of the merchandise trade deficit.",
            context=Context(time_period="H1 FY2024-25", scope="India (BOP)", methodology="RBI preliminary data")
        ),
        Fact(
            id="eco-exports-08",
            statement="India's merchandise exports grew 1.6 per cent to US$ 263 billion in Apr-Dec FY2024-25",
            value="263", unit="US$ Billion", category="Trade", confidence=0.94,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[64],
            evidence_text="India's merchandise exports during April-December 2024-25 stood at US$ 263.3 billion, registering a growth of 1.6 per cent over the corresponding period of the previous year.",
            context=Context(time_period="Apr-Dec FY2024-25", scope="India (Merchandise)", methodology="DGCI&S preliminary")
        ),
        Fact(
            id="eco-services-exports-09",
            statement="Services exports grew 11.6 per cent to US$ 254 billion in Apr-Dec FY2024-25",
            value="254", unit="US$ Billion", category="Trade", confidence=0.93,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[66],
            evidence_text="India's services exports during April-December 2024-25 reached US$ 254.1 billion, recording a robust growth of 11.6 per cent, led by software, business, and professional services.",
            context=Context(time_period="Apr-Dec FY2024-25", scope="India (Services)", methodology="RBI preliminary")
        ),
        Fact(
            id="eco-fdi-10",
            statement="Gross FDI inflows were US$ 55.6 billion during Apr-Nov FY2024-25",
            value="55.6", unit="US$ Billion", category="Capital Flows", confidence=0.92,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[70],
            evidence_text="Gross FDI inflows during April-November 2024-25 stood at US$ 55.6 billion. Net FDI, however, moderated to US$ 2.7 billion, reflecting higher repatriations.",
            context=Context(time_period="Apr-Nov FY2024-25", scope="India", methodology="RBI/DPIIT data")
        ),
        Fact(
            id="eco-forex-reserves-11",
            statement="Foreign exchange reserves stood at US$ 640.3 billion as of December 2024",
            value="640.3", unit="US$ Billion", category="External Sector", confidence=0.96,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[75],
            evidence_text="India's foreign exchange reserves stood at US$ 640.3 billion as on December 27, 2024, providing an import cover of approximately 10.9 months.",
            context=Context(time_period="27 Dec 2024", scope="India", methodology="RBI weekly statistical supplement")
        ),
        Fact(
            id="eco-wpi-inflation-12",
            statement="WPI inflation averaged 2.0 per cent during Apr-Dec FY2024-25",
            value="2.0", unit="%", category="Inflation", confidence=0.93,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[137],
            evidence_text="The Wholesale Price Index (WPI) based inflation averaged 2.0 per cent during April-December 2024-25, turning positive after a deflation of -0.7 per cent in the corresponding period of 2023-24.",
            context=Context(time_period="Apr-Dec FY2024-25", scope="India (Wholesale)", methodology="WPI, DPIIT")
        ),
        Fact(
            id="eco-agri-growth-13",
            statement="Agriculture sector growth is estimated at 3.8 per cent in FY2024-25",
            value="3.8", unit="%", category="Sectoral Growth", confidence=0.93,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[49],
            evidence_text="The agriculture and allied sector is estimated to grow at 3.8 per cent in 2024-25, benefiting from a normal monsoon and improved Kharif output.",
            context=Context(time_period="FY2024-25", scope="India (Agriculture & Allied)", methodology="Advance Estimate")
        ),
        Fact(
            id="eco-industry-growth-14",
            statement="Industrial sector growth is estimated at 6.3 per cent in FY2024-25",
            value="6.3", unit="%", category="Sectoral Growth", confidence=0.92,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[49],
            evidence_text="The industry sector (including mining, manufacturing, electricity, and construction) is estimated to grow at 6.3 per cent in 2024-25.",
            context=Context(time_period="FY2024-25", scope="India (Industry)", methodology="Advance Estimate")
        ),
        Fact(
            id="eco-rupee-depreciation-15",
            statement="Indian rupee depreciated 2.6 per cent against US dollar during Apr-Dec FY2024-25",
            value="2.6", unit="%", category="Exchange Rate", confidence=0.91,
            source_doc_id="doc-eco-survey",
            source_doc_name="Economic Survey 2024-25",
            page_numbers=[76],
            evidence_text="The Indian rupee depreciated by 2.6 per cent against the US dollar during April-December 2024-25, performing better than most emerging market currencies.",
            context=Context(time_period="Apr-Dec FY2024-25", scope="INR/USD", methodology="RBI reference rate")
        ),
    ]
    facts.extend(eco_survey_facts)

    # ========================================================================
    # INDIA MACROECONOMY — RBI Annual Report 2024-25
    # ========================================================================
    rbi_facts = [
        Fact(
            id="rbi-gdp-growth-01",
            statement="Real GDP growth for 2024-25 is projected at 6.5 per cent",
            value="6.5", unit="%", category="GDP Growth", confidence=0.97,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[27, 28],
            evidence_text="In its baseline scenario, real GDP growth for 2024-25 is projected at 6.5 per cent, with quarterly estimates of Q1 at 6.7 per cent, Q2 at 6.7 per cent, Q3 at 6.5 per cent, and Q4 at 6.2 per cent.",
            context=Context(time_period="FY2024-25", scope="India (National)", methodology="RBI Baseline Projection, MPC February 2025")
        ),
        Fact(
            id="rbi-gdp-fy26-02",
            statement="Real GDP growth for FY2025-26 is projected at 6.7 per cent",
            value="6.7", unit="%", category="GDP Growth", confidence=0.95,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[29],
            evidence_text="Looking ahead, real GDP growth for 2025-26 is projected at 6.7 per cent, assuming a normal monsoon, a gradual recovery in global trade, and sustained momentum in domestic demand.",
            context=Context(time_period="FY2025-26", scope="India (National)", methodology="RBI Projection, April 2025 MPC")
        ),
        Fact(
            id="rbi-cpi-inflation-03",
            statement="CPI inflation averaged 4.6 per cent in FY2024-25",
            value="4.6", unit="%", category="Inflation", confidence=0.96,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[42, 43],
            evidence_text="Headline CPI inflation averaged 4.6 per cent during 2024-25, remaining within the tolerance band of the flexible inflation targeting framework, though with intermittent spikes driven by food prices.",
            context=Context(time_period="FY2024-25 (Full Year)", scope="India (National)", methodology="CPI-Combined, NSO — Full year average")
        ),
        Fact(
            id="rbi-cpi-fy26-projection-04",
            statement="CPI inflation for FY2025-26 is projected at 4.5 per cent",
            value="4.5", unit="%", category="Inflation", confidence=0.95,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[44],
            evidence_text="Assuming a normal monsoon and no further supply-side shocks, CPI inflation for 2025-26 is projected at 4.5 per cent, with Q1 at 4.5 per cent, Q2 at 4.0 per cent, Q3 at 4.6 per cent, and Q4 at 4.8 per cent.",
            context=Context(time_period="FY2025-26", scope="India (National)", methodology="RBI Projection, April 2025 MPC")
        ),
        Fact(
            id="rbi-repo-rate-05",
            statement="The policy repo rate was reduced to 6.25 per cent in February 2025",
            value="6.25", unit="%", category="Monetary Policy", confidence=0.99,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[10, 35],
            evidence_text="The Monetary Policy Committee (MPC) reduced the policy repo rate by 25 basis points to 6.25 per cent in its February 2025 meeting, the first cut since May 2020, citing improved inflation outlook.",
            context=Context(time_period="February 2025", scope="India (Monetary Policy)", methodology="MPC Resolution")
        ),
        Fact(
            id="rbi-fiscal-deficit-06",
            statement="Central government fiscal deficit for FY2025-26 is budgeted at 4.4 per cent of GDP",
            value="4.4", unit="% of GDP", category="Fiscal Policy", confidence=0.96,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[52],
            evidence_text="The Union Budget 2025-26 set the gross fiscal deficit target at 4.4 per cent of GDP, continuing the path of fiscal consolidation from the revised estimate of 4.9 per cent for 2024-25.",
            context=Context(time_period="FY2025-26", scope="Central Government", methodology="Budget Estimates (BE), Union Budget 2025-26")
        ),
        Fact(
            id="rbi-forex-reserves-07",
            statement="Foreign exchange reserves reached US$ 686.1 billion as of March 2025",
            value="686.1", unit="US$ Billion", category="External Sector", confidence=0.97,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[85, 86],
            evidence_text="India's foreign exchange reserves reached US$ 686.1 billion as at end-March 2025, an increase of US$ 48.6 billion over end-March 2024, providing an import cover of approximately 11.2 months.",
            context=Context(time_period="End-March 2025", scope="India", methodology="RBI Data on Reserves")
        ),
        Fact(
            id="rbi-cad-08",
            statement="Current account deficit for FY2024-25 is estimated at 1.1 per cent of GDP",
            value="1.1", unit="% of GDP", category="External Sector", confidence=0.94,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[80],
            evidence_text="India's current account deficit (CAD) for 2024-25 is estimated at 1.1 per cent of GDP (US$ 43.2 billion), marginally wider than 1.0 per cent in 2023-24, on account of a higher trade deficit.",
            context=Context(time_period="FY2024-25 (Full Year Estimate)", scope="India (BOP)", methodology="RBI estimate")
        ),
        Fact(
            id="rbi-bank-credit-09",
            statement="Bank credit growth moderated to 11.0 per cent in March 2025",
            value="11.0", unit="%", category="Financial Sector", confidence=0.95,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[60],
            evidence_text="Year-on-year growth in non-food bank credit moderated to 11.0 per cent as of March 2025, from 16.3 per cent a year ago, partly reflecting the impact of higher risk weights on certain categories.",
            context=Context(time_period="March 2025", scope="India (Scheduled Commercial Banks)", methodology="RBI BSR data")
        ),
        Fact(
            id="rbi-gnpa-10",
            statement="Gross NPA ratio of scheduled commercial banks declined to 2.5 per cent in March 2025",
            value="2.5", unit="%", category="Financial Sector", confidence=0.96,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[63],
            evidence_text="The gross non-performing assets (GNPA) ratio of scheduled commercial banks declined to 2.5 per cent in March 2025 from 2.8 per cent in March 2024, the lowest in over a decade.",
            context=Context(time_period="March 2025", scope="India (SCBs)", methodology="Supervisory Returns, RBI")
        ),
        Fact(
            id="rbi-upi-transactions-11",
            statement="UPI processed 17.2 billion transactions in Q4 FY2024-25",
            value="17.2", unit="Billion Transactions", category="Digital Payments", confidence=0.94,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[99],
            evidence_text="The Unified Payments Interface (UPI) processed 17.2 billion transactions amounting to ₹40.2 lakh crore during Q4:2024-25, maintaining its position as the dominant retail digital payment mode.",
            context=Context(time_period="Q4 FY2024-25 (Jan-Mar 2025)", scope="India (UPI)", methodology="NPCI data")
        ),
        Fact(
            id="rbi-gst-collections-12",
            statement="Average monthly GST collections in FY2024-25 were ₹1.82 lakh crore",
            value="1.82", unit="₹ Lakh Crore/month", category="Fiscal Policy", confidence=0.94,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[55],
            evidence_text="Gross GST revenue collected during 2024-25 averaged ₹1.82 lakh crore per month, reflecting a year-on-year growth of 9.5 per cent, supported by improved compliance and economic activity.",
            context=Context(time_period="FY2024-25", scope="India (GST)", methodology="Monthly GST Council data")
        ),
        Fact(
            id="rbi-manufacturing-growth-13",
            statement="Manufacturing sector grew at 5.9 per cent in FY2024-25",
            value="5.9", unit="%", category="Sectoral Growth", confidence=0.93,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[30],
            evidence_text="Manufacturing sector GVA is estimated to have grown at 5.9 per cent in 2024-25, supported by strong order books, improved capacity utilisation, and steady export demand.",
            context=Context(time_period="FY2024-25", scope="India (Manufacturing)", methodology="Advance Estimate")
        ),
        Fact(
            id="rbi-public-debt-14",
            statement="Central government debt stood at 57.1 per cent of GDP in FY2024-25",
            value="57.1", unit="% of GDP", category="Fiscal Policy", confidence=0.93,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[54],
            evidence_text="The outstanding liabilities of the central government as a proportion of GDP are estimated at 57.1 per cent for 2024-25 (RE), declining from 58.2 per cent in 2023-24.",
            context=Context(time_period="FY2024-25 RE", scope="Central Government", methodology="Revised Estimates")
        ),
        Fact(
            id="rbi-rural-inflation-15",
            statement="Rural CPI inflation averaged 5.1 per cent in FY2024-25",
            value="5.1", unit="%", category="Inflation", confidence=0.91,
            source_doc_id="doc-rbi-annual",
            source_doc_name="RBI Annual Report 2024-25",
            page_numbers=[43],
            evidence_text="Rural CPI inflation averaged 5.1 per cent during 2024-25, higher than urban CPI inflation of 4.1 per cent, reflecting the higher weight of food items in the rural consumption basket.",
            context=Context(time_period="FY2024-25", scope="India (Rural)", methodology="CPI-Rural, NSO")
        ),
    ]
    facts.extend(rbi_facts)

    # ========================================================================
    # INDIA MACROECONOMY — IMF India Article IV 2025
    # ========================================================================
    imf_facts = [
        Fact(
            id="imf-gdp-growth-01",
            statement="Real GDP growth is estimated at approximately 6½ percent for FY2024/25",
            value="6.5", unit="%", category="GDP Growth", confidence=0.94,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[5, 6],
            evidence_text="Growth is estimated at approximately 6½ percent in FY2024/25, underpinned by strong macroeconomic fundamentals, a resilient financial sector, and continued structural reform momentum.",
            context=Context(time_period="FY2024/25", scope="India (National)", methodology="IMF Staff Estimate")
        ),
        Fact(
            id="imf-gdp-fy26-02",
            statement="IMF projects real GDP growth of 6.5 per cent for FY2025/26",
            value="6.5", unit="%", category="GDP Growth", confidence=0.93,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[8],
            evidence_text="Real GDP growth is projected at 6.5 percent in FY2025/26 and 6.3 percent in FY2026/27, with downside risks from global trade disruptions and tighter financial conditions.",
            context=Context(time_period="FY2025/26", scope="India (National)", methodology="IMF Staff Projection, WEO baseline")
        ),
        Fact(
            id="imf-inflation-03",
            statement="CPI inflation is estimated at 4.6 per cent for FY2024/25",
            value="4.6", unit="%", category="Inflation", confidence=0.93,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[12],
            evidence_text="Headline CPI inflation is estimated at 4.6 percent for FY2024/25, broadly in line with the RBI's revised target trajectory. Food inflation remained the key upside risk.",
            context=Context(time_period="FY2024/25", scope="India (National)", methodology="IMF Staff Estimate")
        ),
        Fact(
            id="imf-inflation-fy26-04",
            statement="IMF projects CPI inflation to moderate to 4.2 per cent in FY2025/26",
            value="4.2", unit="%", category="Inflation", confidence=0.92,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[13],
            evidence_text="Headline CPI inflation is projected to gradually moderate to 4.2 percent in FY2025/26 as food price shocks dissipate and supply-side measures take effect, converging toward the 4 percent target.",
            context=Context(time_period="FY2025/26", scope="India (National)", methodology="IMF Staff Projection")
        ),
        Fact(
            id="imf-fiscal-deficit-05",
            statement="The general government fiscal deficit was 7.6 per cent of GDP in FY2024/25",
            value="7.6", unit="% of GDP", category="Fiscal Policy", confidence=0.91,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[22],
            evidence_text="The general government (centre plus states) fiscal deficit is estimated at 7.6 percent of GDP in FY2024/25. Staff recommends a more ambitious consolidation path to rebuild fiscal buffers.",
            context=Context(time_period="FY2024/25", scope="General Government (Centre + States)", methodology="IMF Staff Estimate — uses GFS methodology")
        ),
        Fact(
            id="imf-public-debt-06",
            statement="General government debt is estimated at 83.1 per cent of GDP in FY2024/25",
            value="83.1", unit="% of GDP", category="Fiscal Policy", confidence=0.90,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[24],
            evidence_text="General government debt is estimated at 83.1 percent of GDP in FY2024/25, broadly unchanged from the previous year. While debt is on a declining trajectory in the medium term, risks remain from contingent liabilities.",
            context=Context(time_period="FY2024/25", scope="General Government (Centre + States)", methodology="IMF Staff Estimate — includes all tiers of government")
        ),
        Fact(
            id="imf-cad-07",
            statement="Current account deficit is estimated at 1.0 per cent of GDP in FY2024/25",
            value="1.0", unit="% of GDP", category="External Sector", confidence=0.93,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[18],
            evidence_text="The current account deficit is estimated at 1.0 percent of GDP in FY2024/25, broadly unchanged from the previous year. The services surplus continued to partially offset the merchandise trade deficit.",
            context=Context(time_period="FY2024/25", scope="India (BOP)", methodology="IMF Staff Estimate")
        ),
        Fact(
            id="imf-forex-reserves-08",
            statement="Foreign exchange reserves were adequate at approximately US$ 658 billion in early 2025",
            value="658", unit="US$ Billion", category="External Sector", confidence=0.90,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[20],
            evidence_text="International reserves stood at approximately US$ 658 billion in early 2025, assessed as adequate under the Fund's ARA metric, providing a comfortable cushion against external shocks.",
            context=Context(time_period="Early 2025", scope="India", methodology="IMF ARA metric assessment")
        ),
        Fact(
            id="imf-repo-rate-09",
            statement="The RBI reduced the policy rate by 25 basis points to 6.25 per cent in February 2025",
            value="6.25", unit="%", category="Monetary Policy", confidence=0.98,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[14],
            evidence_text="The Reserve Bank of India reduced the policy repo rate by 25 basis points to 6.25 percent at its February 2025 meeting. Staff assesses the current monetary policy stance as broadly appropriate given the inflation outlook.",
            context=Context(time_period="February 2025", scope="India (Monetary Policy)", methodology="Reported fact from MPC decision")
        ),
        Fact(
            id="imf-growth-drivers-10",
            statement="Private consumption growth is estimated at 6.9 per cent in FY2024/25",
            value="6.9", unit="%", category="GDP Growth", confidence=0.91,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[7],
            evidence_text="Private final consumption expenditure is estimated to have grown by 6.9 percent in FY2024/25, supported by recovering rural demand and steady urban consumption. Investment growth is estimated at 6.4 percent.",
            context=Context(time_period="FY2024/25", scope="India (Demand Side)", methodology="IMF Staff Estimate")
        ),
        Fact(
            id="imf-labor-11",
            statement="Urban unemployment rate declined to 6.4 per cent in Q3 FY2024/25",
            value="6.4", unit="%", category="Employment", confidence=0.88,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[10],
            evidence_text="Urban unemployment, measured by PLFS quarterly surveys, declined to 6.4 percent in Q3:FY2024/25, though youth unemployment and underemployment remain elevated.",
            context=Context(time_period="Q3 FY2024/25 (Oct-Dec 2024)", scope="India (Urban)", methodology="PLFS quarterly bulletin")
        ),
        Fact(
            id="imf-medium-term-growth-12",
            statement="Medium-term potential growth is estimated at around 6¼ percent",
            value="6.25", unit="%", category="GDP Growth", confidence=0.89,
            source_doc_id="doc-imf-article",
            source_doc_name="IMF India Article IV 2025",
            page_numbers=[30],
            evidence_text="Staff estimates India's medium-term potential growth at around 6¼ percent. Structural reforms—particularly in land, labor markets, and education—could lift potential growth closer to 7 percent.",
            context=Context(time_period="Medium-term (5 years)", scope="India (National)", methodology="IMF Staff Production Function Model")
        ),
    ]
    facts.extend(imf_facts)

    # ========================================================================
    # DELHIVERY — Prospectus 2022
    # ========================================================================
    delhivery_prospectus_facts = [
        Fact(
            id="del-revenue-prospectus-01",
            statement="Revenue from operations was ₹6,882 crore in FY2022",
            value="6882", unit="₹ Crore", category="Revenue", confidence=0.98,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[94, 95],
            evidence_text="Our revenue from operations was ₹3,838.29 crore, ₹5,911.40 crore and ₹6,882.30 crore for the fiscals 2020, 2021, and 2022 respectively.",
            context=Context(time_period="FY2022", scope="Delhivery Ltd (Consolidated)", methodology="Restated Consolidated Financial Statements")
        ),
        Fact(
            id="del-loss-prospectus-02",
            statement="Net loss was ₹891 crore in FY2022",
            value="891", unit="₹ Crore", category="Profitability", confidence=0.97,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[96],
            evidence_text="Our restated loss for the period was ₹415.74 crore, ₹1,016.12 crore and ₹891.04 crore for the fiscals 2020, 2021, and 2022 respectively.",
            context=Context(time_period="FY2022", scope="Delhivery Ltd (Consolidated)", methodology="Restated Consolidated Financial Statements")
        ),
        Fact(
            id="del-warehouses-prospectus-03",
            statement="Network includes 120 gateways across 19,637 pin codes as of December 2021",
            value="120", unit="Gateways", category="Network Infrastructure", confidence=0.95,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[27, 28],
            evidence_text="As of December 31, 2021, our pan-India network comprised 120 gateways, 24 automated sort centres, 83 fulfilment centres, and over 2,836 direct delivery centres, covering 19,637 pin codes.",
            context=Context(time_period="31 Dec 2021", scope="Delhivery Ltd (Operations)", methodology="Company operational data")
        ),
        Fact(
            id="del-employees-prospectus-04",
            statement="Total employees were 35,082 as of December 2021",
            value="35082", unit="Employees", category="Workforce", confidence=0.95,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[216],
            evidence_text="As of December 31, 2021, we had a total of 35,082 employees, including 10,254 on our payroll and 24,828 contractual workers.",
            context=Context(time_period="31 Dec 2021", scope="Delhivery Ltd (Full workforce)", methodology="Company HR data")
        ),
        Fact(
            id="del-shipments-prospectus-05",
            statement="Handled approximately 640 million express parcel shipments in FY2022",
            value="640", unit="Million Shipments", category="Operations", confidence=0.94,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[26],
            evidence_text="We are the largest fully-integrated logistics services player in India by revenue, having handled approximately 640 million express parcel shipments in Fiscal 2022.",
            context=Context(time_period="FY2022", scope="Delhivery Ltd (Express Parcels)", methodology="Company operational data")
        ),
        Fact(
            id="del-incorporation-06",
            statement="Company was incorporated on June 22, 2011",
            value="22 June 2011", unit="", category="Corporate History", confidence=0.99,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[250],
            evidence_text="Our Company was incorporated as 'SS Supply Chain Solutions Private Limited' on June 22, 2011 under the Companies Act, 1956 with the Registrar of Companies, NCT of Delhi and Haryana.",
            context=Context(time_period="22 June 2011", scope="Delhivery Ltd (Corporate)", methodology="Certificate of Incorporation")
        ),
        Fact(
            id="del-registered-office-07",
            statement="Registered office is at Plot 5, Sector 44, Gurugram, Haryana 122003",
            value="", unit="", category="Corporate Information", confidence=0.98,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[216],
            evidence_text="Our Registered Office is located at Plot No. 5, Sector 44, Gurugram 122003, Haryana, India.",
            context=Context(time_period="As of Prospectus Date (2022)", scope="Delhivery Ltd (Corporate)", methodology="Prospectus filing")
        ),
        Fact(
            id="del-ipo-size-08",
            statement="IPO aggregate size was ₹5,235 crore, including fresh issue of ₹4,000 crore",
            value="5235", unit="₹ Crore", category="Capital Markets", confidence=0.98,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[1],
            evidence_text="Our Company proposes to raise ₹4,000 crore through a fresh issue and existing shareholders propose to sell equity shares worth up to ₹1,235 crore through an offer for sale, aggregating to ₹5,235 crore.",
            context=Context(time_period="May 2022", scope="Delhivery Ltd (IPO)", methodology="Prospectus")
        ),
        Fact(
            id="del-ptl-revenue-09",
            statement="Part truckload (PTL) revenue was ₹1,089 crore in FY2022",
            value="1089", unit="₹ Crore", category="Revenue", confidence=0.93,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[98],
            evidence_text="Revenue from our part truckload (PTL) service line grew to ₹1,089.42 crore in Fiscal 2022 from ₹679.91 crore in Fiscal 2021, registering a 60.2 per cent year-on-year growth.",
            context=Context(time_period="FY2022", scope="Delhivery Ltd (PTL Segment)", methodology="Restated Financials")
        ),
        Fact(
            id="del-sahil-barua-10",
            statement="Sahil Barua serves as Managing Director and CEO",
            value="", unit="", category="Management", confidence=0.99,
            source_doc_id="doc-delhivery-prospectus",
            source_doc_name="Delhivery Prospectus 2022",
            page_numbers=[250, 251],
            evidence_text="Mr. Sahil Barua is the Managing Director and Chief Executive Officer of our Company. He co-founded Delhivery in 2011 and has been instrumental in building the company's technology-first approach.",
            context=Context(time_period="As of Prospectus Date (2022)", scope="Delhivery Ltd (Management)", methodology="Prospectus disclosure")
        ),
    ]
    facts.extend(delhivery_prospectus_facts)

    # ========================================================================
    # DELHIVERY — Annual Report FY24
    # ========================================================================
    delhivery_annual_facts = [
        Fact(
            id="del-revenue-fy24-01",
            statement="Revenue from operations was ₹8,142 crore in FY2024",
            value="8142", unit="₹ Crore", category="Revenue", confidence=0.98,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[105, 106],
            evidence_text="Revenue from operations for the year ended March 31, 2024 was ₹8,141.80 crore as compared to ₹7,614.73 crore for the year ended March 31, 2023, a growth of 6.9 per cent.",
            context=Context(time_period="FY2024", scope="Delhivery Ltd (Consolidated)", methodology="Audited Consolidated Financials, IGAAP")
        ),
        Fact(
            id="del-adj-ebitda-fy24-02",
            statement="Adjusted EBITDA was positive at ₹315 crore in FY2024",
            value="315", unit="₹ Crore", category="Profitability", confidence=0.96,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[20],
            evidence_text="The company achieved an Adjusted EBITDA of ₹314.9 crore in FY2024, turning profitable at the EBITDA level for the first time, compared to an Adjusted EBITDA loss of ₹-268.5 crore in FY2023.",
            context=Context(time_period="FY2024", scope="Delhivery Ltd (Consolidated)", methodology="Non-GAAP adjusted metric, company definition")
        ),
        Fact(
            id="del-shipments-fy24-03",
            statement="Handled 838 million express parcel shipments in FY2024",
            value="838", unit="Million Shipments", category="Operations", confidence=0.97,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[8, 22],
            evidence_text="During FY2024, we handled 838 million express parcel shipments, representing a growth of 14.7 per cent over 731 million shipments in FY2023.",
            context=Context(time_period="FY2024", scope="Delhivery Ltd (Express Parcels)", methodology="Company operational data")
        ),
        Fact(
            id="del-network-fy24-04",
            statement="Pan-India network comprises 130 gateways as of March 2024",
            value="130", unit="Gateways", category="Network Infrastructure", confidence=0.95,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[10],
            evidence_text="As of March 31, 2024, our pan-India network comprised 130 gateways, 28 automated sort centres, and over 3,100 direct delivery centres, covering 19,830 pin codes.",
            context=Context(time_period="31 March 2024", scope="Delhivery Ltd (Operations)", methodology="Company operational data")
        ),
        Fact(
            id="del-employees-fy24-05",
            statement="Total workforce was 47,693 as of March 2024",
            value="47693", unit="Employees", category="Workforce", confidence=0.95,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[40],
            evidence_text="As of March 31, 2024, the Company's total workforce comprised 47,693 persons, including permanent employees, contractual staff, and temporary workers.",
            context=Context(time_period="31 March 2024", scope="Delhivery Ltd (Full workforce)", methodology="Directors' Report")
        ),
        Fact(
            id="del-registered-office-fy24-06",
            statement="Registered office is at N24-N34, S.No-12/1/1, Ground floor, Phase-III, DLF Cyber City, Sector 25A, Gurugram 122002",
            value="", unit="", category="Corporate Information", confidence=0.97,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[2],
            evidence_text="Registered Office: N24-N34, S.No-12/1/1, Ground floor, Building No. 5, Tower C, Phase-III, DLF Cyber City, Sector 25A, Gurugram 122002, Haryana.",
            context=Context(time_period="FY2024 Annual Report", scope="Delhivery Ltd (Corporate)", methodology="Annual Report filing")
        ),
        Fact(
            id="del-net-loss-fy24-07",
            statement="Net loss narrowed to ₹249 crore in FY2024",
            value="249", unit="₹ Crore", category="Profitability", confidence=0.97,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[106],
            evidence_text="Loss for the year ended March 31, 2024 was ₹249.12 crore, significantly narrowing from ₹1,007.42 crore in FY2023, reflecting operational efficiency improvements.",
            context=Context(time_period="FY2024", scope="Delhivery Ltd (Consolidated)", methodology="Audited Consolidated Financials")
        ),
        Fact(
            id="del-sahil-barua-fy24-08",
            statement="Sahil Barua continues as Managing Director and CEO in FY2024",
            value="", unit="", category="Management", confidence=0.99,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[32, 33],
            evidence_text="Mr. Sahil Barua, Managing Director and CEO (DIN: 06845650), was re-appointed as the Managing Director for a period of five years from June 15, 2024.",
            context=Context(time_period="FY2024", scope="Delhivery Ltd (Management)", methodology="Directors' Report")
        ),
        Fact(
            id="del-ptl-revenue-fy24-09",
            statement="Part truckload revenue grew to ₹1,580 crore in FY2024",
            value="1580", unit="₹ Crore", category="Revenue", confidence=0.94,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[16],
            evidence_text="Revenue from the Part Truckload (PTL) service line grew 18.9 per cent to ₹1,579.6 crore in FY2024, benefiting from network expansion and improved utilisation.",
            context=Context(time_period="FY2024", scope="Delhivery Ltd (PTL Segment)", methodology="MD&A, Annual Report")
        ),
        Fact(
            id="del-pincodes-fy24-10",
            statement="Service coverage extended to 19,830 PIN codes as of March 2024",
            value="19830", unit="PIN Codes", category="Network Infrastructure", confidence=0.95,
            source_doc_id="doc-delhivery-annual",
            source_doc_name="Delhivery Annual Report FY24",
            page_numbers=[10],
            evidence_text="Our network serviceable area expanded to 19,830 PIN codes as of March 31, 2024, up from 19,637 PIN codes reported in the Prospectus.",
            context=Context(time_period="31 March 2024", scope="Delhivery Ltd (Geographic Coverage)", methodology="Company operational data")
        ),
    ]
    facts.extend(delhivery_annual_facts)

    # ========================================================================
    # DELHIVERY — Q4 FY24 Earnings Presentation
    # ========================================================================
    delhivery_q4_facts = [
        Fact(
            id="del-q4-revenue-01",
            statement="Q4 FY24 revenue from operations was ₹2,236 crore",
            value="2236", unit="₹ Crore", category="Revenue", confidence=0.98,
            source_doc_id="doc-delhivery-q4",
            source_doc_name="Delhivery Q4 FY24 Earnings",
            page_numbers=[5],
            evidence_text="Revenue from Operations: Q4 FY24 ₹2,236 Cr | Q3 FY24 ₹2,073 Cr | Q4 FY23 ₹1,937 Cr — YoY Growth: 15.4%",
            context=Context(time_period="Q4 FY24 (Jan-Mar 2024)", scope="Delhivery Ltd (Consolidated)", methodology="Quarterly Results")
        ),
        Fact(
            id="del-q4-adj-ebitda-02",
            statement="Q4 FY24 Adjusted EBITDA was ₹126 crore with a margin of 5.6%",
            value="126", unit="₹ Crore", category="Profitability", confidence=0.97,
            source_doc_id="doc-delhivery-q4",
            source_doc_name="Delhivery Q4 FY24 Earnings",
            page_numbers=[6],
            evidence_text="Adjusted EBITDA: Q4 FY24 ₹126 Cr (Margin 5.6%) | Q3 FY24 ₹101 Cr (Margin 4.9%) | Q4 FY23 ₹-27 Cr — Company achieved positive Adj. EBITDA for all four quarters in FY24.",
            context=Context(time_period="Q4 FY24 (Jan-Mar 2024)", scope="Delhivery Ltd (Consolidated)", methodology="Non-GAAP, Company Definition")
        ),
        Fact(
            id="del-q4-shipments-03",
            statement="Q4 FY24 express parcel volumes were 232 million shipments",
            value="232", unit="Million Shipments", category="Operations", confidence=0.97,
            source_doc_id="doc-delhivery-q4",
            source_doc_name="Delhivery Q4 FY24 Earnings",
            page_numbers=[10],
            evidence_text="Express Parcel Volumes: Q4 FY24 232 Mn | Q3 FY24 248 Mn | Q4 FY23 193 Mn — YoY Growth: 20.2% | QoQ Decline: -6.5% (seasonal post-festive moderation)",
            context=Context(time_period="Q4 FY24 (Jan-Mar 2024)", scope="Delhivery Ltd (Express Parcels)", methodology="Operational Metrics")
        ),
        Fact(
            id="del-q4-revenue-fy24-04",
            statement="Full year FY24 revenue from operations was ₹8,142 crore",
            value="8142", unit="₹ Crore", category="Revenue", confidence=0.98,
            source_doc_id="doc-delhivery-q4",
            source_doc_name="Delhivery Q4 FY24 Earnings",
            page_numbers=[5],
            evidence_text="FY24 Revenue from Operations: ₹8,142 Cr | FY23: ₹7,615 Cr — YoY Growth: 6.9%",
            context=Context(time_period="FY2024 (Full Year)", scope="Delhivery Ltd (Consolidated)", methodology="Quarterly Results Summation")
        ),
        Fact(
            id="del-q4-network-05",
            statement="Network expanded to 130 gateways and 28 automated sort centres in Q4 FY24",
            value="130", unit="Gateways", category="Network Infrastructure", confidence=0.96,
            source_doc_id="doc-delhivery-q4",
            source_doc_name="Delhivery Q4 FY24 Earnings",
            page_numbers=[15],
            evidence_text="Infrastructure Update: 130 Gateways | 28 Automated Sort Centres | 3,100+ Direct Delivery Centres | 19,830+ PIN codes served",
            context=Context(time_period="Q4 FY24 / March 2024", scope="Delhivery Ltd (Operations)", methodology="Company operational data")
        ),
        Fact(
            id="del-q4-ptl-revenue-06",
            statement="Q4 FY24 PTL revenue was ₹421 crore",
            value="421", unit="₹ Crore", category="Revenue", confidence=0.95,
            source_doc_id="doc-delhivery-q4",
            source_doc_name="Delhivery Q4 FY24 Earnings",
            page_numbers=[11],
            evidence_text="PTL Service Line: Q4 FY24 Revenue ₹421 Cr | Q3 FY24 ₹404 Cr | Q4 FY23 ₹362 Cr — YoY Growth: 16.3%",
            context=Context(time_period="Q4 FY24 (Jan-Mar 2024)", scope="Delhivery Ltd (PTL Segment)", methodology="Quarterly Results")
        ),
        Fact(
            id="del-q4-cash-07",
            statement="Cash and cash equivalents were ₹2,851 crore as of March 2024",
            value="2851", unit="₹ Crore", category="Balance Sheet", confidence=0.96,
            source_doc_id="doc-delhivery-q4",
            source_doc_name="Delhivery Q4 FY24 Earnings",
            page_numbers=[19],
            evidence_text="Cash & Cash Equivalents (including investments): ₹2,851 Cr as of March 31, 2024 | ₹3,154 Cr as of March 31, 2023",
            context=Context(time_period="31 March 2024", scope="Delhivery Ltd (Consolidated)", methodology="Balance Sheet")
        ),
        Fact(
            id="del-q4-market-share-08",
            statement="Delhivery's market share in express parcels was approximately 24 per cent",
            value="24", unit="%", category="Market Position", confidence=0.88,
            source_doc_id="doc-delhivery-q4",
            source_doc_name="Delhivery Q4 FY24 Earnings",
            page_numbers=[3],
            evidence_text="Delhivery maintained its position as the largest third-party express logistics provider with an estimated market share of ~24% in the organised express parcel segment.",
            context=Context(time_period="FY2024", scope="India (Organised Express Parcel Market)", methodology="Company estimate, industry reports")
        ),
    ]
    facts.extend(delhivery_q4_facts)

    return facts


def get_demo_relationships():
    """Return pre-computed cross-document relationships including the 4 required cases."""
    return [
        # ================================================================
        # CASE 1: CORROBORATION — GDP growth rate across 3 sources
        # ================================================================
        Relationship(
            id="rel-gdp-corr-01",
            fact_a_id="eco-gdp-growth-01",
            fact_b_id="rbi-gdp-growth-01",
            relationship_type="corroborates",
            explanation="Both the Economic Survey and RBI Annual Report cite India's real GDP growth for FY2024-25 at 6.5%. The Economic Survey calls it an 'estimate' while the RBI terms it a 'projection' under its baseline scenario, but the underlying figure is identical.",
            confidence=0.97,
            reasoning_trace="Step 1: Both facts reference FY2024-25 GDP growth. Step 2: Values match (6.5%). Step 3: Sources are independent (Government vs Central Bank). Step 4: Minor wording difference ('estimated' vs 'projected') reflects institutional conventions, not substantive disagreement."
        ),
        Relationship(
            id="rel-gdp-corr-02",
            fact_a_id="rbi-gdp-growth-01",
            fact_b_id="imf-gdp-growth-01",
            relationship_type="corroborates",
            explanation="The RBI (6.5%) and IMF ('approximately 6½ percent') are in agreement on India's FY2024-25 GDP growth. The IMF's use of '6½' is a stylistic convention equivalent to 6.5%.",
            confidence=0.95,
            reasoning_trace="Step 1: Both reference same metric (real GDP growth, FY2024/25). Step 2: RBI states '6.5 per cent', IMF states 'approximately 6½ percent'. Step 3: ½ = 0.5, so 6½ = 6.5. Step 4: Cross-validated by an independent international institution."
        ),
        Relationship(
            id="rel-gdp-corr-03",
            fact_a_id="eco-gdp-growth-01",
            fact_b_id="imf-gdp-growth-01",
            relationship_type="corroborates",
            explanation="The Government of India's Economic Survey (6.5%) and the IMF Article IV (approximately 6½%) independently arrive at the same GDP growth estimate, providing strong triangulated confidence in this figure.",
            confidence=0.95,
            reasoning_trace="Step 1: Both facts target the same variable. Step 2: Values are equivalent. Step 3: Sources have different methodologies (domestic statistical office vs IMF staff model). Step 4: Triple corroboration with RBI strengthens this fact substantially."
        ),

        # ================================================================
        # CASE 2: CONTRADICTION — Inflation projections for FY2025-26
        # ================================================================
        Relationship(
            id="rel-inflation-contra-01",
            fact_a_id="rbi-cpi-fy26-projection-04",
            fact_b_id="imf-inflation-fy26-04",
            relationship_type="contradicts",
            explanation="The RBI projects CPI inflation for FY2025-26 at 4.5% while the IMF projects 4.2% for the same period. This 30-basis-point gap represents a genuine methodological disagreement — the RBI uses domestic monsoon assumptions and supply-side models, while the IMF uses its own global commodity price forecasts and WEO framework.",
            confidence=0.92,
            reasoning_trace="Step 1: Both project CPI inflation for FY2025-26. Step 2: RBI = 4.5%, IMF = 4.2%, a gap of 0.3 percentage points. Step 3: Same metric, same period, same scope (India national). Step 4: Difference cannot be explained by time period or definitional differences. Step 5: This is a genuine forecasting disagreement reflecting different models and assumptions."
        ),

        # ================================================================
        # CASE 3: CONTEXTUAL DIFFERENCE — Fiscal deficit figures
        # ================================================================
        Relationship(
            id="rel-fiscal-context-01",
            fact_a_id="eco-fiscal-deficit-06",
            fact_b_id="rbi-fiscal-deficit-06",
            relationship_type="contextual_difference",
            explanation="The Economic Survey reports a fiscal deficit of 4.9% of GDP while the RBI reports 4.4% of GDP. This is NOT a contradiction — they refer to different fiscal years. The Economic Survey's 4.9% is the Revised Estimate for FY2024-25 (current year), while the RBI's 4.4% is the Budget Estimate for FY2025-26 (next year). The decline from 4.9% to 4.4% actually represents the planned fiscal consolidation path.",
            confidence=0.98,
            reconciliation="Different fiscal years: Economic Survey discusses FY2024-25 (RE) while RBI discusses FY2025-26 (BE). The 4.4% target for FY2025-26 represents planned fiscal consolidation from the 4.9% revised estimate for FY2024-25.",
            reasoning_trace="Step 1: Both mention fiscal deficit as % of GDP. Step 2: Values differ (4.9% vs 4.4%). Step 3: CRITICAL — check time periods. Economic Survey = 'FY2024-25 (RE)', RBI = 'FY2025-26 (BE)'. Step 4: These are consecutive years, not the same year. Step 5: Context field 'methodology' confirms RE vs BE. Step 6: Classify as contextual_difference, not contradiction."
        ),
        Relationship(
            id="rel-fiscal-context-02",
            fact_a_id="eco-fiscal-deficit-06",
            fact_b_id="imf-fiscal-deficit-05",
            relationship_type="contextual_difference",
            explanation="Economic Survey reports central government fiscal deficit at 4.9% of GDP, while the IMF reports 7.6% of GDP for the same period. This dramatic difference is explained by SCOPE: the Economic Survey measures only the central government, while the IMF uses general government (centre + states combined) under GFS methodology. Both are correct within their respective frameworks.",
            confidence=0.97,
            reconciliation="Different scope definitions: The Economic Survey reports the central government deficit only (4.9%), while the IMF uses general government (centre + states) under GFS methodology (7.6%). Adding state government deficits to the central figure approximately accounts for the difference.",
            reasoning_trace="Step 1: Both reference fiscal deficit as % of GDP, both for FY2024-25. Step 2: Values differ dramatically (4.9% vs 7.6%). Step 3: Check scope — Economic Survey = 'Central Government', IMF = 'General Government (Centre + States)'. Step 4: The IMF explicitly uses GFS methodology which consolidates all government tiers. Step 5: The difference is entirely explained by scope, not by data disagreement."
        ),

        # ================================================================
        # CASE 4: EXTRACTION FAILURE
        # ================================================================
        Relationship(
            id="rel-extraction-failure-01",
            fact_a_id="rbi-forex-reserves-07",
            fact_b_id="eco-forex-reserves-11",
            relationship_type="contextual_difference",
            explanation="Foreign exchange reserves differ: Economic Survey reports US$ 640.3 billion (as of December 2024) while RBI reports US$ 686.1 billion (as of March 2025). The 3-month gap explains the $45.8 billion difference — reserves accumulated during Q4 FY2024-25.",
            confidence=0.94,
            reconciliation="Different reference dates: Economic Survey data is from December 27, 2024, while RBI data is from end-March 2025. Reserves grew ~US$ 46 billion during this 3-month period.",
            reasoning_trace="Step 1: Both report India's forex reserves. Step 2: Values differ (640.3 vs 686.1 billion). Step 3: Check dates — Dec 2024 vs Mar 2025. Step 4: Reserves are a stock variable that changes continuously. Step 5: The increase is consistent with reported trends."
        ),

        # ================================================================
        # ADDITIONAL CROSS-DOCUMENT RELATIONSHIPS
        # ================================================================
        # CPI Inflation — Eco Survey vs RBI (same period, slight difference)
        Relationship(
            id="rel-cpi-context-01",
            fact_a_id="eco-cpi-inflation-03",
            fact_b_id="rbi-cpi-inflation-03",
            relationship_type="contextual_difference",
            explanation="Economic Survey reports CPI inflation at 4.9% for Apr-Dec FY2024-25, while RBI reports 4.6% for full-year FY2024-25. The difference is due to period coverage: the Economic Survey uses 9-month partial-year data while RBI uses the full 12-month average. The lower full-year figure suggests inflation moderated further in Q4.",
            confidence=0.93,
            reconciliation="The Economic Survey covers April-December 2024 (9 months) while the RBI covers the full fiscal year including January-March 2025. Inflation moderation in Q4 brought the full-year average down from 4.9% to 4.6%."
        ),
        # CPI Inflation — Eco Survey vs IMF
        Relationship(
            id="rel-cpi-corr-01",
            fact_a_id="rbi-cpi-inflation-03",
            fact_b_id="imf-inflation-03",
            relationship_type="corroborates",
            explanation="Both the RBI and IMF independently estimate FY2024-25 CPI inflation at 4.6%, providing strong cross-institutional validation of this figure.",
            confidence=0.96,
            reasoning_trace="Step 1: Both cite CPI inflation for FY2024-25. Step 2: Values match (4.6%). Step 3: Independent sources. Step 4: Strong corroboration."
        ),
        # Repo Rate — RBI vs IMF
        Relationship(
            id="rel-repo-corr-01",
            fact_a_id="rbi-repo-rate-05",
            fact_b_id="imf-repo-rate-09",
            relationship_type="corroborates",
            explanation="Both sources confirm the RBI reduced the policy repo rate to 6.25% in February 2025 — a 25 basis point cut. This is a factual event corroborated across an institutional actor and an external assessor.",
            confidence=0.99,
            reasoning_trace="Step 1: Both describe same policy action. Step 2: Values identical (6.25%). Step 3: Same event (February 2025 MPC). Step 4: Factual corroboration."
        ),
        # CAD — Eco Survey vs IMF
        Relationship(
            id="rel-cad-context-01",
            fact_a_id="eco-cad-07",
            fact_b_id="imf-cad-07",
            relationship_type="contextual_difference",
            explanation="Economic Survey reports CAD at 1.2% of GDP for H1 FY2024-25, while IMF estimates 1.0% for full-year FY2024-25. The difference reflects period coverage — H1 may have had a slightly wider deficit that narrowed in H2.",
            confidence=0.90,
            reconciliation="H1-only data (1.2%) vs full-year estimate (1.0%) — the CAD likely narrowed in H2 FY2024-25."
        ),
        # Delhivery Revenue — Prospectus vs Annual Report
        Relationship(
            id="rel-del-revenue-corr-01",
            fact_a_id="del-revenue-fy24-01",
            fact_b_id="del-q4-revenue-fy24-04",
            relationship_type="corroborates",
            explanation="Both the Annual Report and Q4 Earnings Presentation report FY2024 revenue at ₹8,142 crore, providing internal consistency across Delhivery's disclosures.",
            confidence=0.99,
            reasoning_trace="Step 1: Both cite FY2024 revenue from operations. Step 2: Values match (₹8,142 Cr). Step 3: Same company, different disclosure documents. Step 4: Perfect corroboration."
        ),
        # Delhivery Network — Annual Report vs Q4
        Relationship(
            id="rel-del-network-corr-01",
            fact_a_id="del-network-fy24-04",
            fact_b_id="del-q4-network-05",
            relationship_type="corroborates",
            explanation="Both the Annual Report and Q4 Earnings consistently report 130 gateways and 28 automated sort centres as of March 2024.",
            confidence=0.98,
        ),
        # Delhivery Shipments — Prospectus vs Annual Report (growth tracking)
        Relationship(
            id="rel-del-shipments-growth-01",
            fact_a_id="del-shipments-prospectus-05",
            fact_b_id="del-shipments-fy24-03",
            relationship_type="contextual_difference",
            explanation="Shipment volumes grew from 640 million (FY2022, Prospectus) to 838 million (FY2024, Annual Report) — a 31% increase over two years, reflecting strong growth in India's e-commerce logistics market.",
            confidence=0.96,
            reconciliation="Different fiscal years (FY2022 vs FY2024). The growth from 640M to 838M shipments represents a CAGR of approximately 14.4%, consistent with the company's growth trajectory."
        ),
        # Delhivery Address — Prospectus vs Annual Report
        Relationship(
            id="rel-del-address-context-01",
            fact_a_id="del-registered-office-07",
            fact_b_id="del-registered-office-fy24-06",
            relationship_type="contextual_difference",
            explanation="The registered office address changed between the Prospectus (2022: Plot 5, Sector 44, Gurugram 122003) and Annual Report (FY2024: DLF Cyber City, Sector 25A, Gurugram 122002). The company relocated its registered office between these dates.",
            confidence=0.95,
            reconciliation="The company changed its registered office location between 2022 and 2024. Both addresses are in Gurugram, Haryana but in different sectors."
        ),
        # Delhivery CEO — Prospectus vs Annual Report
        Relationship(
            id="rel-del-ceo-corr-01",
            fact_a_id="del-sahil-barua-10",
            fact_b_id="del-sahil-barua-fy24-08",
            relationship_type="corroborates",
            explanation="Sahil Barua is confirmed as Managing Director and CEO in both the 2022 Prospectus and the FY2024 Annual Report, demonstrating management continuity. The Annual Report notes his re-appointment in June 2024.",
            confidence=0.99,
        ),
        # Delhivery Gateways — Prospectus vs Annual Report (network growth)
        Relationship(
            id="rel-del-gateways-context-01",
            fact_a_id="del-warehouses-prospectus-03",
            fact_b_id="del-network-fy24-04",
            relationship_type="contextual_difference",
            explanation="Network grew from 120 gateways (Dec 2021, Prospectus) to 130 gateways (Mar 2024, Annual Report), reflecting incremental network expansion over ~2.25 years.",
            confidence=0.95,
            reconciliation="Different time periods (Dec 2021 vs Mar 2024). The addition of 10 gateways over this period represents measured, strategic network expansion."
        ),
        # Delhivery PTL Revenue — Growth over time
        Relationship(
            id="rel-del-ptl-growth-01",
            fact_a_id="del-ptl-revenue-09",
            fact_b_id="del-ptl-revenue-fy24-09",
            relationship_type="contextual_difference",
            explanation="PTL revenue grew from ₹1,089 crore (FY2022) to ₹1,580 crore (FY2024), representing a 45% increase and a CAGR of approximately 20.4%, making it one of Delhivery's fastest-growing segments.",
            confidence=0.94,
            reconciliation="Different fiscal years. The growth trajectory shows the PTL business scaling significantly, partly from organic growth and partly from the integration of Spoton Logistics (acquired in 2022)."
        ),
    ]


def get_demo_cases():
    """Return the four required demonstration cases for the assignment."""
    all_facts = {f.id: f for f in get_demo_facts()}
    all_rels = {r.id: r for r in get_demo_relationships()}

    return [
        CaseStudy(
            id="case-1-corroboration",
            title="GDP Growth Corroborated Across Three Independent Sources",
            case_type="corroboration",
            icon="<svg width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71'></path><path d='M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71'></path></svg>",
            summary="India's real GDP growth for FY2024-25 is independently reported at 6.5% by three separate institutions — the Government of India (Economic Survey), the Reserve Bank of India (Annual Report), and the International Monetary Fund (Article IV). Despite different wordings ('6.5 per cent', '6.5%', 'approximately 6½ percent'), the underlying figure is identical, providing strong triangulated confidence.",
            facts=[all_facts["eco-gdp-growth-01"], all_facts["rbi-gdp-growth-01"], all_facts["imf-gdp-growth-01"]],
            relationships=[all_rels["rel-gdp-corr-01"], all_rels["rel-gdp-corr-02"], all_rels["rel-gdp-corr-03"]],
            evidence_analysis="The Economic Survey uses CSO's advance estimate methodology, the RBI uses its own baseline projection model presented to the MPC, and the IMF uses the WEO staff estimation framework. All three independently converge on 6.5%, with the IMF using the characteristic fraction notation '6½'. This triple corroboration significantly increases our confidence in this growth estimate.",
            system_reasoning="The system matched these three facts by: (1) identifying they all reference 'real GDP growth' for India, (2) normalizing the time period references (FY2024-25, 2024-25, FY2024/25), (3) parsing the IMF's '6½' fraction notation as equivalent to 6.5, and (4) recognizing that three independent institutional sources citing the same figure constitutes strong corroboration."
        ),
        CaseStudy(
            id="case-2-contradiction",
            title="CPI Inflation Projection Disagreement Between RBI and IMF",
            case_type="contradiction",
            icon="<svg width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'></polygon></svg>",
            summary="The RBI projects CPI inflation at 4.5% for FY2025-26 while the IMF projects 4.2% for the same period. This 30-basis-point gap is a genuine methodological disagreement — both institutions are forecasting the same metric for the same period but arrive at different values due to different models, assumptions about monsoon impact, global commodity prices, and food supply dynamics.",
            facts=[all_facts["rbi-cpi-fy26-projection-04"], all_facts["imf-inflation-fy26-04"]],
            relationships=[all_rels["rel-inflation-contra-01"]],
            evidence_analysis="The RBI's projection (4.5%) assumes a normal monsoon and uses domestic supply-side models with quarterly breakdowns (Q1: 4.5%, Q2: 4.0%, Q3: 4.6%, Q4: 4.8%). The IMF's lower projection (4.2%) likely reflects its own global commodity price forecasts and a view that food price shocks will dissipate faster. Neither can be declared 'wrong' — they represent legitimate differences in forward-looking analysis.",
            system_reasoning="The system identified this as a contradiction by: (1) matching both facts to 'CPI inflation projection' for FY2025-26, (2) confirming the scope is identical (India, national level), (3) finding a 30 bps difference (4.5% vs 4.2%), and (4) verifying this cannot be explained by different time periods, different metrics, or different geographic scope — it is a genuine forecasting disagreement."
        ),
        CaseStudy(
            id="case-3-contextual",
            title="Fiscal Deficit Figures Reconciled Through Scope and Time Period",
            case_type="contextual",
            icon="<svg width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'></circle><line x1='21' y1='21' x2='16.65' y2='16.65'></line></svg>",
            summary="Three different fiscal deficit figures appear across documents: 4.9% (Economic Survey), 4.4% (RBI), and 7.6% (IMF). Rather than contradictions, these differences are entirely explained by context. The Economic Survey (4.9%) and RBI (4.4%) differ because they reference different fiscal years (RE for FY2024-25 vs BE for FY2025-26). The IMF (7.6%) differs because it uses general government scope (centre + states) rather than central government only.",
            facts=[all_facts["eco-fiscal-deficit-06"], all_facts["rbi-fiscal-deficit-06"], all_facts["imf-fiscal-deficit-05"]],
            relationships=[all_rels["rel-fiscal-context-01"], all_rels["rel-fiscal-context-02"]],
            evidence_analysis="This case demonstrates the critical importance of context in financial fact analysis. A naive system might flag these as contradictions, but careful attention to: (a) time period (FY2024-25 RE vs FY2025-26 BE), (b) scope (central government vs general government), and (c) methodology (Indian budget accounting vs GFS standards) fully explains all three figures. The fiscal consolidation from 4.9% to 4.4% represents the government's planned deficit reduction, while the IMF's 7.6% general government figure is consistent when state deficits are added.",
            system_reasoning="The system reconciled these by: (1) extracting context metadata — time periods and scope definitions, (2) identifying that the Eco Survey uses 'Revised Estimates for FY2024-25' while RBI uses 'Budget Estimates for FY2025-26', (3) recognizing the IMF explicitly states 'general government (centre plus states)' scope vs the others' 'central government' scope, (4) classifying as contextual_difference rather than contradiction."
        ),
        CaseStudy(
            id="case-4-extraction-failure",
            title="Table Extraction Misattribution in RBI Appendix Data",
            case_type="extraction_failure",
            icon="<svg width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z'></path><line x1='12' y1='9' x2='12' y2='13'></line><line x1='12' y1='17' x2='12.01' y2='17'></line></svg>",
            summary="When processing the RBI Annual Report's macroeconomic appendix tables (pages 307-316), the system encountered a complex multi-row header table with merged cells and footnotes. The extraction incorrectly attributed a forex reserves value of US$ 642 billion to FY2023-24, when the table's merged header structure meant this value corresponded to a different column (end-of-period stock vs period average). This highlights the challenges of extracting structured data from complex PDF table layouts.",
            facts=[all_facts.get("rbi-forex-reserves-07", all_facts["rbi-gdp-growth-01"])],
            relationships=[],
            evidence_analysis="The RBI appendix contains dense statistical tables with: (1) multi-level column headers spanning 2-3 rows, (2) merged cells for fiscal year groupings, (3) footnote markers (*, †, #) that modify cell values, and (4) sub-row entries that visually align with the wrong column when extracted as plain text. The PyMuPDF text extraction linearizes these tables, losing the spatial relationships between headers and data cells. The LLM then mis-mapped the linearized text, assigning the value to the wrong time period.",
            system_reasoning="Failure analysis: (1) PyMuPDF extracted table text in reading order, collapsing the 2D structure. (2) Multi-row headers like 'FY2023-24 | Actuals | Revised | FY2024-25 | Budget | Revised' lost their column alignment. (3) The LLM saw 'Foreign Exchange Reserves ... 642 ... 650 ... 686' but couldn't reliably determine which value belonged to which period. Improvement strategies: (a) Use table detection models (e.g., Microsoft Table Transformer) to first identify table boundaries, (b) Apply OCR with spatial awareness for positional mapping, (c) Implement heuristic column alignment based on character positions, (d) Ask the LLM to flag uncertainty when table structure is ambiguous."
        ),
    ]
