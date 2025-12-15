import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import fitz  # PyMuPDF
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Telecom BI Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
CONFIG = {
    "GEMINI_API_KEY": st.secrets.get("GEMINI_API_KEY", ""),
    "POWERBI_URL": "https://app.powerbi.com/reportEmbed?reportId=dac16af5-864a-4155-9cf1-30e2a12ef3f6&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730"
}

class TelecomApp:
    def __init__(self):
        self.setup_styling()
        self.setup_gemini()
    
    def setup_styling(self):
        """Configure professional CSS styling"""
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }
        .feature-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #1f77b4;
            margin: 1rem 0;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        .chat-user {
            background-color: #e3f2fd;
            border-left: 4px solid #1f77b4;
        }
        .chat-assistant {
            background-color: #f5f5f5;
            border-left: 4px solid #4caf50;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_gemini(self):
        """Initialize Gemini AI model"""
        try:
            genai.configure(api_key=CONFIG["GEMINI_API_KEY"])
            self.model = genai.GenerativeModel('gemini-2.5-pro')
        except Exception as e:
            st.error(f"Gemini AI configuration failed: {e}")
            self.model = None
    
    @st.cache_data
    def load_pdf_context(_self):
        """Load and process PDF documents"""
        pdf_dir = Path(__file__).parent / "pdf"
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            st.warning("No PDF files found in the 'pdf' directory")
            return None
        
        documents = []
        for pdf_path in pdf_files:
            try:
                with fitz.open(pdf_path) as doc:
                    text = "\n".join(page.get_text() for page in doc)
                    documents.append(f"DOCUMENT: {pdf_path.name}\n{text}\n")
            except Exception as e:
                st.warning(f"Failed to read {pdf_path.name}: {e}")
        
        return "\n".join(documents) if documents else None
    
    def generate_ai_response(self, user_query):
        """Generate AI response with PDF context"""
        if not self.model:
            return "AI service unavailable. Please check configuration."
        
        pdf_context = self.load_pdf_context()
        if not pdf_context:
            return self.get_fallback_response()
        
        system_prompt = f"""
        You are a telecom data analyst specializing in Tunisian market data from INTT reports.
        
        CONTEXT:
        {pdf_context}
        
        INSTRUCTIONS:
        - Answer using ONLY the provided context
        - Cite source documents: [filename.pdf]
        - Focus on: revenues, market shares, investments, operator performance
        - Be precise and professional
        - Use bullet points for lists
        
        QUESTION: {user_query}
        
        ANSWER:
        """
        
        try:
            response = self.model.generate_content(system_prompt)
            return response.text if response.text else "No response generated."
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def get_fallback_response(self):
        """Return fallback response when PDFs aren't loaded"""
        return """
        **Telecom Market Overview** (Based on typical INTT data):
        
        - **Total Market Revenue (2024)**: ~3,989 M.TND
        - **Major Operators**: Orange (23%), Ooredoo (38%), Tunisie Telecom (32%)
        - **Key Services**: Mobile Data, Fixed Telephony, Broadband
        - **Market Trends**: Data service growth (+22.7%), Voice service decline (-3.2%)
        
        *For precise, cited data, please ensure PDF documents are in the 'pdf' folder.*
        """

class PageRenderer:
    def __init__(self, telecom_app):
        self.app = telecom_app
    
    def render_sidebar(self):
        """Render application sidebar"""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center;">
                <h3>🏢 Telecom Intelligence</h3>
                <p>Huawei EBG Tunisia</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            
            page = st.radio(
                "Navigation",
                ["🏠 Dashboard", "📈 BI Reports", "🤖 AI Analyst", "📊 Data Explorer"],
                key="nav"
            )
            
            # PDF status
            if self.app.load_pdf_context():
                st.success("✅ PDFs Loaded")
                if st.button("🔄 Reload Documents"):
                    st.cache_data.clear()
                    st.rerun()
            
            st.markdown("---")
            st.markdown("""
            **Final Year Project**  
            Business Intelligence & AI  
            Esprit School of Business
            """)
            
            return page
    
    def render_home(self):
        """Render dashboard homepage"""
        st.markdown('<div class="main-header">Telecom Market Intelligence Platform</div>', unsafe_allow_html=True)
        
        # Key metrics
        cols = st.columns(4)
        metrics = [
            ("Market Revenue", "3,989 M.TND", "+4.5%"),
            ("Investments", "757 M.TND", "+17.6%"),
            ("Data Growth", "22.7%", "YoY"),
            ("Efficiency", "5.3x", "Rev/Inv")
        ]
        
        for col, (title, value, delta) in zip(cols, metrics):
            with col:
                st.metric(title, value, delta)
        
        st.markdown("---")
        
        # Project overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 Project Overview")
            st.markdown("""
            **Enhancing Telecom Data Access Through Conversational AI and BI Dashboards**
            
            This platform demonstrates the synergy between traditional Business Intelligence 
            and modern AI technologies for telecom market analysis:
            
            - **Power BI Dashboards**: Interactive visual analytics
            - **AI Chatbot**: Natural language querying with source citations
            - **Data Democratization**: Accessible to technical and non-technical users
            - **Real INTT Data**: Grounded in official Tunisian telecom reports
            
            **Technical Stack**: Python, Power BI, PostgreSQL, Talend ETL, Gemini AI
            """)
        
        with col2:
            st.markdown("### 🚀 Quick Access")
            st.info("""
            **Get Started:**
            1. View BI Reports for visual analysis
            2. Ask AI Analyst specific questions
            3. Explore data trends
            """)
    
    def render_bi_reports(self):
        """Render Power BI dashboard"""
        st.markdown("### 📊 Interactive BI Dashboard")
        
        components.iframe(
            src=CONFIG["POWERBI_URL"],
            width=1140,
            height=700,
            scrolling=True
        )
        
        # Dashboard guidance
        with st.expander("💡 Dashboard Guide"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **How to Use:**
                - Use filters for specific time periods
                - Click charts for drill-through
                - Compare operator performance
                - Export insights for reporting
                """)
            with col2:
                st.markdown("""
                **Key Analyses:**
                - Market share evolution
                - Revenue by service type
                - Investment trends
                - Operator benchmarking
                """)
    
    def render_ai_analyst(self):
        """Render AI chatbot interface"""
        st.markdown("### 🤖 Telecom AI Analyst")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! I'm your Telecom AI Analyst. I can answer questions about market data, operator performance, and trends from INTT reports. How can I assist you?"}
            ]
        
        # Display chat
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about telecom data..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Generate and display response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing telecom data..."):
                    response = self.app.generate_ai_response(prompt)
                    st.markdown(response)
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Quick questions
        st.markdown("---")
        st.markdown("#### 💡 Sample Questions")
        
        questions = [
            "What are the current market shares?",
            "How has Orange's revenue evolved?",
            "Compare operator investments",
            "Show data service growth trends"
        ]
        
        cols = st.columns(4)
        for col, question in zip(cols, questions):
            with col:
                if st.button(question, key=f"q_{question}"):
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    st.rerun()
        
        if st.button("🗑️ Clear Conversation", type="secondary"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Conversation cleared. How can I help you?"}
            ]
            st.rerun()
    
    def render_data_explorer(self):
        """Render data visualization explorer"""
        st.markdown("### 📈 Data Explorer")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            metric = st.selectbox("Metric", ["Revenue", "Market Share", "Investments"])
        with col2:
            operators = st.multiselect("Operators", ["Orange", "Ooredoo", "Tunisie Telecom"], default=["Orange", "Ooredoo", "Tunisie Telecom"])
        with col3:
            years = st.slider("Years", 2017, 2024, (2020, 2024))
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(self.create_revenue_trend(), use_container_width=True)
        
        with col2:
            st.plotly_chart(self.create_market_share(), use_container_width=True)
        
        # Data table
        st.markdown("#### Sample Data")
        st.dataframe(self.get_sample_data(), use_container_width=True)
    
    def create_revenue_trend(self):
        """Create revenue trend visualization"""
        fig = go.Figure()
        
        operator_data = {
            "Orange": [720, 750, 780, 800, 805],
            "Ooredoo": [1200, 1250, 1260, 1270, 1280],
            "Tunisie Telecom": [1050, 1100, 1150, 1200, 1280]
        }
        
        colors = {"Orange": "#FF6B00", "Ooredoo": "#C70039", "Tunisie Telecom": "#1F77B4"}
        
        for operator, revenues in operator_data.items():
            fig.add_trace(go.Scatter(
                x=[2020, 2021, 2022, 2023, 2024],
                y=revenues,
                name=operator,
                line=dict(color=colors[operator], width=3),
                mode='lines+markers'
            ))
        
        fig.update_layout(title="Operator Revenue Trends (M.TND)", xaxis_title="Year", yaxis_title="Revenue")
        return fig
    
    def create_market_share(self):
        """Create market share visualization"""
        fig = px.pie(
            values=[38, 32, 23, 7],
            names=['Ooredoo', 'Tunisie Telecom', 'Orange', 'Others'],
            title='Market Share Distribution 2024',
            color_discrete_sequence=['#C70039', '#1F77B4', '#FF6B00', '#888888']
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    
    def get_sample_data(self):
        """Generate sample telecom data"""
        return pd.DataFrame({
            'Year': [2022, 2023, 2024] * 3,
            'Operator': ['Orange']*3 + ['Ooredoo']*3 + ['Tunisie Telecom']*3,
            'Revenue_M_TND': [780, 800, 805, 1260, 1270, 1280, 1150, 1200, 1280],
            'Market_Share_%': [23, 22, 23, 38, 38, 38, 32, 32, 32],
            'Service': ['Total'] * 9
        })

def main():
    """Main application entry point"""
    app = TelecomApp()
    renderer = PageRenderer(app)
    
    # Navigation
    page = renderer.render_sidebar()
    
    # Page routing
    if page == "🏠 Dashboard":
        renderer.render_home()
    elif page == "📈 BI Reports":
        renderer.render_bi_reports()
    elif page == "🤖 AI Analyst":
        renderer.render_ai_analyst()
    elif page == "📊 Data Explorer":
        renderer.render_data_explorer()

if __name__ == "__main__":
    main()