import string

import folium
import plotly.express as px
import spacy
import streamlit as st
from folium.plugins import MarkerCluster
from nltk.corpus import stopwords
nltk.download('stopwords')
from utils.utils import block
nlp = spacy.load('fr_core_news_sm')
stop = set(stopwords.words('french'))
exclude = set(string.punctuation)


@st.cache_data(ttl=82800 * 3)
def execute_block1(tanit_df):
    """Executes block1"""

    viz_snippet1 = '''
    filtered_df = tanit_df[tanit_df['Category'].notna()]
    category_counts = filtered_df.groupby('Category')['Openings'].sum()
    
    category_counts_df = category_counts.reset_index()
    category_counts_df.columns = ['Category', 'Count']
    
    fig = px.pie(category_counts_df, values='Count', names='Category', title='Distribution of Job Categories',
                hole=0.5)
    
    fig.update_traces(textinfo='percent+label') 
    fig.update_layout(
           autosize=True,
           margin=dict(l=20, r=20, t=30, b=20),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.show()
'''

    st.code(viz_snippet1)
    filtered_df = tanit_df[tanit_df['Category'].notna()]
    category_counts = filtered_df.groupby('Category')['Openings'].sum()

    category_counts_df = category_counts.reset_index()
    category_counts_df.columns = ['Category', 'Count']

    fig = px.pie(category_counts_df, values='Count', names='Category', title='Distribution of Job Categories',
                 hole=0.5)

    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


@st.cache_data(ttl=82800 * 3)
def execute_block2(tanit_df):
    block2 = block('Visualizing the concentration of jobs across the country.', )
    block2.render()

    filtered_df = tanit_df[(tanit_df['Latitude'].notna()) & (tanit_df['Category'].notna())]

    m = folium.Map(location=[36.806389, 10.181667], zoom_start=6, tiles='cartodbpositron')
    mc = MarkerCluster()

    for idx, row in filtered_df.iterrows():
        mc.add_child(folium.Marker([row['Latitude'], row['Longitude']]))

    m.add_child(mc)
    return m


@st.cache_data(ttl=82800 * 3)
def execute_block3(tanit_df):
    viz_snippet = '''
        filtered_df = tanit_df[ (tanit_df['Salary Range'] != 'Confidentiel') & (tanit_df['Salary Range'].notna()) & (tanit_df['Category'] != 'Other')]
        filtered_df = filtered_df.groupby(['Salary Range','Category']).size().reset_index(name='count')
        fig = px.bar(filtered_df, x='count', y='Category', color='Salary Range',
                     title='Distribution of Salary Ranges by Category',
                     barmode='stack',color_discrete_sequence = px.colors.sequential.Sunset)
        fig.update_layout(
            autosize=True,
            xaxis_title='Number of Job Postings',
            yaxis_title='Category',
            legend_title='Salary Range',
            yaxis_type='category',
            font=dict(
                family='Times New Roman',
                size=14,
                color='#7f7f7f'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500  # Adjust the height as needed
            ,yaxis={'categoryorder':'total ascending'}
        )

        fig.show()'''

    Block = block('Analysis of salary information', viz_snippet)
    Block.render()

    filtered_df = tanit_df[(tanit_df['Salary Range'] != 'Confidentiel') & (tanit_df['Salary Range'].notna()) & (
            tanit_df['Category'] != 'Other')]

    filtered_df = filtered_df.groupby(['Salary Range', 'Category']).size().reset_index(name='count')

    fig = px.bar(
        filtered_df,
        x='count',
        y='Category',
        color='Salary Range',
        title='Distribution of Salary Ranges by Category',
        barmode='stack',
        color_discrete_sequence=px.colors.sequential.Sunset
    )

    fig.update_layout(
        autosize=True,

        xaxis_title='Number of Job Postings',
        yaxis_title='Category',
        legend_title='Salary Range',
        yaxis_type='category',
        font=dict(
            family='Times New Roman',
            size=14,
            color='#7f7f7f'
        ),

        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder': 'total ascending'}
    )
    return fig


@st.cache_data(ttl=82800 * 3)
def execute_block4(tanit_df):
    viz_snippet3 = '''
        df = tanit_df.explode('Language_list')
        language_counts = df.groupby(['Category', 'Language_list']).size().reset_index(name='Count')
        language_counts= language_counts[(~language_counts['Category'].isin(['Other'])) & (language_counts['Language_list'].isin(['Arabe','Français','Anglais']))]
        fig = px.bar(language_counts, x='Count', y='Category', color='Language_list', barmode='stack')
        fig.update_layout(yaxis={'categoryorder':'total ascending'},height=450)
        fig.show()'''
    Block = block('Most common language requirements across categories', viz_snippet3)
    Block.render()
    df = tanit_df.explode('Language_list')
    language_counts = df.groupby(['Category', 'Language_list']).size().reset_index(name='Count')
    language_counts = language_counts[(~language_counts['Category'].isin(['Other'])) & (
        language_counts['Language_list'].isin(['Arabe', 'Français', 'Anglais']))]
    fig = px.bar(language_counts, x='Count', y='Category', color='Language_list', barmode='stack')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


@st.cache_data(ttl=82800 * 3)
def execute_block5(tanit_df):
    viz_snippet4 = '''
            filtered_df = tanit_df[tanit_df['Category'] != 'Other']
            experience_counts=filtered_df.groupby(['Category','Experience']).size().reset_index(name="count").
            fig = px.bar(experience_counts, x='count', y='Category', color='Experience',
                         title='Experience Required by Job Category',
                         barmode='stack',color_discrete_sequence = px.colors.sequential.Sunset)
            fig.update_layout(
                autosize=True,
                xaxis_title='Number of Job Postings',
                yaxis_title='Category',
                legend_title='Experience',
                yaxis_type='category',
                font=dict(
                    family='Times New Roman',
                    size=14,
                    color='#7f7f7f'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=450 ,yaxis={'categoryorder':'total ascending'}

            )

            fig.show() '''
    Block = block('Previous experience requirements across job categories', viz_snippet4)

    Block.render()

    filtered_df = tanit_df[tanit_df['Category'] != 'Other']
    experience_counts = filtered_df.groupby(['Category', 'Experience']).size().reset_index(name="count")
    fig = px.bar(experience_counts, x='count', y='Category', color='Experience',
                 title='Experience Required by Job Category',
                 barmode='stack', color_discrete_sequence=px.colors.sequential.Sunset)
    fig.update_layout(
        autosize=True,
        xaxis_title='Number of Job Postings',
        yaxis_title='Category',
        legend_title='Experience',
        yaxis_type='category',
        font=dict(
            family='Times New Roman',
            size=14,
            color='#7f7f7f'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder': 'total ascending'}

    )
    return fig


@st.cache_data(ttl=82800 * 3)
def execute_block6(tanit_df):
    viz_snippet5 = '''
        exploded_df = tanit_df.explode('contract_types')
        grouped_df = exploded_df.groupby(['contract_types', 'posting_date']).size().reset_index(name='count')
        grouped_df = grouped_df[grouped_df['contract_types'].isin(['SIVP','Contrat al Karama','Temps partiel'])]

        fig = px.line(grouped_df, x='posting_date', y='count', color='contract_types',
                      title='Entry-level Job Postings Over Time by Contract Type',
                      labels={'posting_date': 'Posting Date', 'count': 'Number of Postings', 'contract_types': 'Contract Type'},height=450)

        fig.update_layout(xaxis_title='Posting Date', yaxis_title='Number of Postings')

        fig.show()
        '''
    Block = block('Entry-level/Internship postings timeline', viz_snippet5)
    Block.render()

    exploded_df = tanit_df.explode('contract_types')
    grouped_df = exploded_df.groupby(['contract_types', 'posting_date']).size().reset_index(name='count')
    grouped_df = grouped_df[grouped_df['contract_types'].isin(['SIVP', 'Contrat al Karama', 'Temps partiel'])]

    fig = px.line(grouped_df, x='posting_date', y='count', color='contract_types',
                  title='Entry-level Job Postings Over Time by Contract Type',
                  labels={'posting_date': 'Posting Date', 'count': 'Number of Postings',
                          'contract_types': 'Contract Type'}, height=450)

    fig.update_layout(xaxis_title='Posting Date', yaxis_title='Number of Postings')
    return fig


@st.cache_data(ttl=82800 * 3)
def execute_block7(tanit_df):
    viz_snippet6 = '''
        exploded_df = tanit_df.explode('contract_types')


        internship_df = exploded_df[(exploded_df['Experience'].isin(['No experience','0-1 year','1-3 years','3-5 years']))&(exploded_df['contract_types'].isin(['SIVP','Contrat al Karama'])) & (exploded_df['Category'].isin(['Accounting','Finance','Engineering','Marketing','Software/IT'])) ]



        grouped_df = internship_df.groupby(['Category', 'Experience','contract_types']).size().reset_index(name='count')
        grouped_df = grouped_df[grouped_df['Experience'].isin(['No experience','0-1 year','1-3 years','3-5 years'])]

        fig = px.bar(grouped_df, x='Category', y='count', color='Experience', barmode='group',facet_col='contract_types',
                     title='Experience requirements for entry-level contracts across different categories',
                     labels={'Category': 'Category', 'count': 'Number of Postings', 'Experience': 'Experience Required'},height=500,color_discrete_sequence = px.colors.sequential.Sunset)

        fig.update_layout(xaxis_title='Category', yaxis_title='Number of Postings')
        fig.update_yaxes(matches=None)
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("contract_types=", "")))

        fig.show()

    '''
    Block = block("Do you need experience to land your first job out of university/Internship?", viz_snippet6)
    Block.render()

    exploded_df = tanit_df.explode('contract_types')

    internship_df = exploded_df[
        (exploded_df['Experience'].isin(['No experience', '0-1 year', '1-3 years', '3-5 years'])) & (
            exploded_df['contract_types'].isin(['SIVP', 'Contrat al Karama'])) & (
            exploded_df['Category'].isin(['Accounting', 'Finance', 'Engineering', 'Marketing', 'Software/IT']))]

    grouped_df = internship_df.groupby(['Category', 'Experience', 'contract_types']).size().reset_index(name='count')
    grouped_df = grouped_df[grouped_df['Experience'].isin(['No experience', '0-1 year', '1-3 years', '3-5 years'])]

    fig = px.bar(grouped_df, x='Category', y='count', color='Experience', barmode='group', facet_col='contract_types',
                 title='Experience requirements for entry-level contracts across different categories',
                 labels={'Category': 'Category', 'count': 'Number of Postings', 'Experience': 'Experience Required'},
                 height=500, color_discrete_sequence=px.colors.sequential.Sunset)

    fig.update_layout(xaxis_title='Category', yaxis_title='Number of Postings')
    fig.update_yaxes(matches=None)
    fig.for_each_annotation(lambda a: a.update(text=a.text.replace("contract_types=", "")))
    return fig

@st.cache_data(ttl=82800 * 3)
def execute_block8(tanit_df):
    viz_snippet7 = '''
        ed_levels = tanit_df.explode("education_levels")
        ed_levels1 = ed_levels.groupby(['Category','education_levels']).size().reset_index(name="count")
        ed_levels1 = ed_levels1[(ed_levels1['education_levels'].isin(['Master','Ingénieur','Licence']))&(ed_levels1['Category'].isin(['Accounting','Finance','Engineering','Marketing','Software/IT']))]
        fig = px.bar(ed_levels1, y='count', x='Category', color='education_levels', barmode='group')
        fig.update_layout(yaxis={'categoryorder':'total ascending'},height=500)
        fig.show()'''
    Block = block('Degree requirements by job category',viz_snippet7)
    Block.render()
    ed_levels = tanit_df.explode("education_levels")
    ed_levels1 = ed_levels.groupby(['Category', 'education_levels']).size().reset_index(name="count")
    ed_levels1 = ed_levels1[(ed_levels1['education_levels'].isin(['Master', 'Ingénieur', 'Licence'])) & (
        ed_levels1['Category'].isin(['Accounting', 'Finance', 'Engineering', 'Marketing', 'Software/IT']))]
    fig = px.bar(ed_levels1, y='count', x='Category', color='education_levels', barmode='group',
                 color_discrete_sequence=px.colors.sequential.Sunset)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    return fig

@st.cache_data(ttl=82800 * 3)
def execute_block9(tanit_df):
    viz_snippet8 = '''
        filtered_df = ed_levels[(ed_levels['Category'].isin(['Finance','Engineering','Marketing','Software/IT']))&(ed_levels['education_levels'].isin(['Master','Ingénieur','Licence',"Grandes Ecoles"]))&(ed_levels["Salary Range"] != "Confidentiel")]
        filtered_df['Experience'] = filtered_df['Experience'].map(experience_map)
        desired_order = ['No experience','0-1 year','1-3 years','3-5 years','5-10 years','10+ years']
        filtered_df['Experience'] = pd.Categorical(filtered_df['Experience'], categories=desired_order, ordered=True)

        filtered_df['Experience'] = filtered_df['Experience'].cat.reorder_categories(desired_order)
        filtered_df = filtered_df.groupby(['Category','Salary Range','education_levels']).size().reset_index(name="count")
        fig= px.bar(filtered_df, x='Salary Range', y='count', color='education_levels', barmode='group', facet_col='Category',
                     title='Job Postings by Salary Range and Education Levels Across Categories',facet_col_wrap=2,
                     labels={'Salary Range': 'Salary Range', 'count': 'Number of Postings', 'education_levels': 'Education Level', 'Category': 'Category'})

        fig.update_layout(
            autosize=True,
            yaxis={'categoryorder': 'total ascending'},
            height=700
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("Category=", "")))'''
    Block = block('Salaries by degree type across industries',viz_snippet8)
    Block.render()
    ed_levels = tanit_df.explode("education_levels")
    filtered_df = ed_levels[(ed_levels['Category'].isin(['Finance', 'Engineering', 'Marketing', 'Software/IT'])) & (
        ed_levels['education_levels'].isin(['Master', 'Ingénieur', 'Licence', "Grandes Ecoles"])) & (
                                    ed_levels["Salary Range"] != "Confidentiel")]
    filtered_df = filtered_df.groupby(['Category', 'Salary Range', 'education_levels']).size().reset_index(name="count")
    fig = px.bar(filtered_df, x='Salary Range', y='count', color='education_levels', barmode='group',
                 facet_col='Category',
                 title='Job Postings by Salary Range and Education Levels Across Categories', facet_col_wrap=2,
                 labels={'Salary Range': 'Salary Range', 'count': 'Number of Postings',
                         'education_levels': 'Education Level', 'Category': 'Category'},
                 color_discrete_sequence=px.colors.sequential.Sunset)

    fig.update_layout(
        autosize=True,
        yaxis={'categoryorder': 'total ascending'},
        height=700
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.replace("Category=", "")))
    return fig

@st.cache_data(ttl=82800 * 3)
def execute_block10(tanit_df):
    viz_snippet9 = '''programming_keywords = {
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'typescript', 'go', 'r', 'scala', 'perl', 'rust', 'dart', 'matlab', 'html',
        'css', 'sql', 'node.js', 'react', 'angular', 'vue', 'django', 'flask', 'spring',
        'rails', 'laravel', 'asp.net', 'tensorflow', 'pytorch', 'keras', 'theano',
        'hadoop', 'spark', 'scikit-learn', 'pandas', 'numpy', 'xgboost', 'lightgbm',
        'aws', 'azure', 'gcp', 'google cloud', 'amazon web services', 'microsoft azure',
        'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'puppet', 'chef',
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova', 'ionic', 'objective-c'
        }

        def extract_keywords(text):
            doc = nlp(text.lower())
            relevant_words = [token.text for token in doc if token.text in programming_keywords]
            return relevant_words

        category = 'Software/IT'
        filtered_df = tanit_df[tanit_df['Category'] == category]

        filtered_df['combined_text'] = (
            filtered_df['Title'].fillna('') + ' ' +
            filtered_df['Description'].fillna('') + ' ' +
            filtered_df['Requirements'].fillna('')
        )

        filtered_df['keywords'] = filtered_df['combined_text'].apply(lambda x: extract_keywords(str(x)))

        exploded_df = filtered_df.explode('keywords')

        keyword_counts = exploded_df['keywords'].value_counts().reset_index()
        keyword_counts.columns = ['keyword', 'count']

        top_keywords = keyword_counts.head(30)

        fig = px.bar(top_keywords, x='count', y='keyword', orientation='h',
                     title=f'Top Technologies/Frameworks in Job Listings for {category}',
                     labels={'count': 'Frequency', 'keyword': 'Technologies/Frameworks'},
                     color='count')

        fig.update_layout(
            xaxis_title='Frequency',
            yaxis_title='Technologies/Frameworks',
            yaxis={'categoryorder': 'total ascending'},
            coloraxis_showscale=False,
            height=800,
        )'''
    Block = block('Software/IT Frameworks Requirements',viz_snippet9)
    Block.render()
    programming_keywords = {
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'typescript', 'go', 'r', 'scala', 'perl', 'rust', 'dart', 'matlab', 'html',
        'css', 'sql', 'node.js', 'react', 'angular', 'vue', 'django', 'flask', 'spring',
        'rails', 'laravel', 'asp.net', 'tensorflow', 'pytorch', 'keras', 'theano',
        'hadoop', 'spark', 'scikit-learn', 'pandas', 'numpy', 'xgboost', 'lightgbm',
        'aws', 'azure', 'gcp', 'google cloud', 'amazon web services', 'microsoft azure',
        'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'puppet', 'chef',
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova', 'ionic', 'objective-c'
    }

    def extract_keywords(text):
        doc = nlp(text.lower())
        relevant_words = [token.text for token in doc if token.text in programming_keywords]
        return relevant_words

    category = 'Software/IT'
    filtered_df = tanit_df[tanit_df['Category'] == category]

    filtered_df['combined_text'] = (
            filtered_df['Title'].fillna('') + ' ' +
            filtered_df['Description'].fillna('') + ' ' +
            filtered_df['Requirements'].fillna('')
    )

    filtered_df['keywords'] = filtered_df['combined_text'].apply(lambda x: extract_keywords(str(x)))

    exploded_df = filtered_df.explode('keywords')

    keyword_counts = exploded_df['keywords'].value_counts().reset_index()
    keyword_counts.columns = ['keyword', 'count']

    top_keywords = keyword_counts.head(30)

    fig = px.bar(top_keywords, x='count', y='keyword', orientation='h',
                 title=f'Top Technologies/Frameworks in Job Listings for {category}',
                 labels={'count': 'Frequency', 'keyword': 'Technologies/Frameworks'},
                 color='count')

    fig.update_layout(
        xaxis_title='Frequency',
        yaxis_title='Technologies/Frameworks',
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False,
        height=800,
    )
    return fig



