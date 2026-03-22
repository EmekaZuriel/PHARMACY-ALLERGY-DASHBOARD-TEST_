import streamlit as st
import base64
import pandas as pd

st.set_page_config(page_title= 'CLINICAL DRUG ALLERGY SYSTEM', layout='wide')

#BACKGROUND + UI STYLING

def get_base64(file):
    with open(file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

    
    

         
            
                
    
    
                    


st.markdown('''
    <style>
    stApp .block-container {
       background-color: #ffffff !important;
       color: #1f2d3d !important;
       padding: 30px;
       border-radius: 15px;
       }
       
       stMetric-value, stMetric-label {
       color: #1f2d3d !important;
          }
          
        .stDataFrame td, .sdDataFrame th {
            color: #1f2d3d !important;
            background-color: #ffffff !important;
            }
        </style>
        ''',unsafe_allow_html=True)

#DATABASES
allergy_db= {
    'Amoxicillin':{'class':'Penicillin','severity':'Severe'},
    'Procaine_penicillin': {'class':'Penicillin','severity':'Severe'},
    'Fansidar':{'class':'Sulphonamides','severity':'Severe'},
    'Septrin':{'class':'Sulphonamides', 'severity':'Severe'},
    'Ibuprofen':{'class': 'NSAIDs','severity':'Moderate'},
    'Aspirin' :{'class':'NSAIDs','severity':'Moderate'}
}

cross_reactivity = {
    'Penicillin':['Procaine_penicillin','Amoxicillin'],
    'Sulphonamides' :['Fansidar', 'Septrin'],
    'NSAIDs': ['Ibuprofen','Aspirin']

}

alternatives= {
    'Penicillin':['Azithromycin','Ciprofloxacin','Nitrofurantoin'],
    'Sulphonamides':['Eryt            hromycin','Proguanil'],
    'NSAIDs':['paracetamol','co_codamol','tramadol']
}

inventory=['Azithromycin','Ciprofloxacin','Nitrofurantoin','Erythromycin','Proguanil','paracetamol','co_codamol','tramadol']

#SESSION STATE
if 'history' not in st.session_state:
    st.session_state.history =[]

if 'last_result' not in st.session_state:
    st.session_state.last_result=None

#TITLE
st.markdown(
    "<h1 style='text-align:center;'>PHARMACY CLINICAL DECISION SUPPORT SYSTEM</h1",
    unsafe_allow_html=True
)
st.markdown('---')

#TABS
tab1,tab2,tab3=st.tabs(["input","Results","Dashboard"])

#TAB 1 INPUT
with tab1:
    st.subheader('Enter Prescription Details')

    patient_id= st.text_input('Patient ID')
    drugs= st.text_area('Drugs (comma separated)')

    if st.button('Analyse Prescription'):
        if patient_id=='' or drugs=='':
            st.warning('Missing input')
            st.session_state.last_result=None
        else:
            drug_list= [d.strip().title() for d in drugs.split(',')]
            unknown_drugs= [d for d in drug_list if d not in allergy_db]

            if unknown_drugs:
                result= {
                    'status': 'deferred',
                    'message': f'Uknown drugs: {unknown_drugs}'
                }

            else:
                results=[]
                explanations=[]
                alternatives_list=[]
                allergy_found=False

                for drug in drug_list:
                    if drug in allergy_db:
                        allergy_found=True
                        drug_class=allergy_db[drug]['class']
                        severity= allergy_db[drug]['severity']

                        explanations.append(
                            f'{drug} ; {drug_class} class ({severity} risk)'
                        )
                        if drug_class in alternatives:
                            for alt in alternatives[drug_class]:
                                if alt in inventory:
                                    alternatives_list.append(alt)
                        results.append({
                            "Drug":drug,
                            "Class": drug_class,
                            "Severity": severity
                        })
                result= {
                    'status': 'allergy'if allergy_found else 'safe',
                    'data':results,
                    'explanations':explanations,
                    'alternatives': list(set(alternatives_list))
                }
                st.session_state.history.append({
                    'patient':patient_id,
                    'allergy': allergy_found
                })
            st.session_state.last_result= result
            st.success('ANALYSIS COMPLETE:CHECK RESULT TAB')

#TAB 2 RESULTS
with tab2:
    st.subheader('PHARMACY CLINICAL DECISION OUTPUT')
    result=st.session_state.last_result

    if result is None:
        st.info('No analysis yet')
    else:
        if result["status"]=="deferred":
            st.warning(f'Decision Deferred: {result['message']}')
        elif result["status"]=="safe":
            st.success('No Allergy Risk Detected')
        else:
            st.error('ALLERGY RISK DETECTED')
            df= pd.DataFrame(result['data'])
            st.dataframe(df)

            st.markdown('### Explanation')
            for exp in result['explanations']:
                st.write(f' {exp}')

            if result['alternatives']:
                st.markdown('### Recommended Alternatives')
                st.success(','.join(result['alternatives']))

