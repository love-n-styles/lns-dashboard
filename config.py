import streamlit as st
import plotly.express as px


class Config:

    @classmethod
    def default_chart_margins(self):
        return dict(l=60, r=10, t=45, b=30)

    @classmethod
    def set_chart_config(self, fig: px.line, *args, **kwargs):
        xtick = kwargs.get('xtick', 1)
        ytick = kwargs.get('ytick', 0)
        fig.update_layout(margin=Config.default_chart_margins())
        if xtick == 0:
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="grey")
        else:
            fig.update_xaxes(showgrid=True, gridwidth=1,
                             gridcolor="grey", dtick=xtick)
        if ytick == 0:
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="grey")
        else:
            fig.update_yaxes(showgrid=True, gridwidth=1,
                             gridcolor="grey", dtick=ytick)
        return fig

    @classmethod
    def placeholder(self, title="Placeholder"):
        st.markdown(f"<h3 style='color:grey'><i>{title}</i></h3>",
                    unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
                width: 100%;">
            <h1 style='text-align: center; color: #00b300;'>&nbsp</h1>
            </div>
            """, unsafe_allow_html=True)

    @classmethod
    def show_no_record_found(self):
        st.markdown(f"<div style='color:red'>No record found.<div>",
                    unsafe_allow_html=True)
