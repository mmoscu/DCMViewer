import streamlit as st
from src.utils import *
import gc

# Hide FileUploader deprecation
st.set_option('deprecation.showfileUploaderEncoding', False)
icon = Image.open("eye.png")
st.set_page_config(
    page_title="DCMViewer",
    page_icon=icon,
)

# Hide streamlit header
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

data_key = 'has_data'
width = 500 # width of shown images
data_is_ready = False
data_has_changed = False

if not os.path.isdir('./data/'):
    os.makedirs('./data/')

#if os.path.isdir('./data/'):
#    clear_data_storage('./data/')
#os.makedirs('./data/')

if not os.path.isdir('./temp'):
    os.makedirs('./temp/')

# Adjusting images to be centered.
with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)
    
if __name__ == "__main__": 
    
    state = get_state()

    state(stored_anomalyes_ = ["Anomaly1", "Anomaly2", "Anomaly3"])

    st.title('DICOM Viewer Lite')

    st.sidebar.title('DICOM Labeling Tool')

    #demo_button = st.sidebar.checkbox('Demo', value=False)
    
    url_input = st.sidebar.text_input('Enter the Google Drive shared URL for the .dcm files')
    
    st.sidebar.markdown('<h5>MAX FILE SIZE: 100 MB (server-dependent)</h5>', unsafe_allow_html=True)
    st.sidebar.markdown(' ')
    st.sidebar.markdown('or')

    file_uploaded =  st.sidebar.file_uploader("Upload a .zip with .dcm files", type="zip")

    #if demo_button:
    #    url_input = 'https://drive.google.com/file/d/1ESRZpJA92g8L4PqT2adCN3hseFbnw9Hg/view?usp=sharing'

    if file_uploaded:
        if not state[data_key]:
            if does_zip_have_dcm(file_uploaded):
                store_data(file_uploaded)
                data_has_changed = True
                st.success("Data loaded")

    if url_input:
        if not state[data_key]:
            if download_zip_from_url(url_input):
                data_has_changed = True
                st.success("Data loaded")

    if st.sidebar.button('---------- Refresh input data ----------'):
        clear_data_storage(temp_data_directory + get_report_ctx().session_id + '/')
        clear_data_storage(temp_zip_folder)
        st.caching.clear_cache()
        url_input = st.empty()
        data_is_ready = False
        data_has_changed = False
        state[data_key] = False
        state.clear()

    if data_has_changed:
        valid_folders = get_DCM_valid_folders(temp_data_directory + get_report_ctx().session_id + '/')
        
        for folder in valid_folders:
            state[folder.split('/')[-1]] = ('', '', {'Anomaly': '', 'Slices': ''})

        state[data_key] = True
        state['valid_folders'] = valid_folders
        state.last_serie = ''

        data_has_changed = False
    
    if state[data_key]:
        data_is_ready = True
    
    if data_is_ready:

        series_names = get_series_names(state['valid_folders'])
        
        selected_serie = st.selectbox('Select a series', series_names, index=0)
        
        st.markdown('<h2>Patient Information</h2>', unsafe_allow_html=True)
        display_info = st.checkbox('Display data', value=False)
        
        if state.last_serie != selected_serie:
            st.caching.clear_cache()
            state.last_serie = selected_serie

        if selected_serie is None:
            st.error("No valid folders found. Please upload a .zip archive containing a folder with a valid serie name and refresh input data.")
        img3d, info = processing_data(state['valid_folders'][series_names.index(selected_serie)] + '/')


        if display_info:
            st.dataframe(info)

        st.markdown('<h1>VISUALIZATION AREA</h1>', unsafe_allow_html=True)

        view = st.radio('Select 2D or 3D view',["2D View","3D View"])    
        if view == "3D View":
            thresh_3D = st.slider(
                    'Visualization threshold (Houndsfeld units)',
                    int(np.min(img3d)), int(np.max(img3d)), min((int(np.max(img3d)) - int(np.min(img3d)))//2, 450)
                )
            st.plotly_chart(build_3D(img3d,thresh_3D))

        else:

            options = st.multiselect('Select 2D views of the DICOM', 
                                    ['Axial', 'Coronal', 'Sagittal'], 
                                    ['Axial'])
            
            state(coronal_slice_ = (img3d.shape[0] + 1)//2) # setting and getting eventual state-related values
            coronal_slice = state["coronal_slice_"]

            if 'Axial' in options:
                st.markdown('<h2>Axial view</h2>', unsafe_allow_html=True)

                #st.number_input('Enter a number',min_value=1,max_value=img3d.shape[2],step=1)

                axial_slider = st.slider(
                    'Axial Slices',
                    1, img3d.shape[2], (img3d.shape[2] + 1)//2
                )-1

                axial_max = int(img3d[:, :, axial_slider].max())
                axial_min = int(img3d[:, :, axial_slider].min())
                axial_threshold_tuple = st.slider(
                    'Axial Color Threshold',
                    0, 100, (40, 60)
                )
                axial_threshold = [0,0]
                axial_threshold[0],axial_threshold[1] = axial_threshold_tuple
                axial_threshold[1] = axial_max * ((2 * axial_threshold[1] / 100) - 1)
                axial_threshold[0] = axial_min * ((2 * axial_threshold[0] / 100) - 1)

                img_view = normalize_image(filter_image2(axial_threshold, img3d[:, :, axial_slider]))

                anno = st.button("Annotate on image")
                if anno:
                    # figure for editing
                    fig_axial = px.imshow(img_view, #x="Xposition", y="Yposition",
                                #hover_data={z: False},
                                color_continuous_scale='gray', title="Interactive Annotation")
                    
                    fig_axial.update_layout(coloraxis_showscale=False)
                    fig_axial.update_xaxes(showticklabels=False)
                    fig_axial.update_yaxes(showticklabels=False)
                    fig_axial.update_layout(clickmode='event+select',
                                dragmode='drawline',
                                newshape=dict(line_color='red'))
                    fig_axial.show(config={'modeBarButtonsToAdd':['drawline',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ], 'displaylogo': False,
                                       'scrollZoom': True,
                                       'toImageButtonOptions': {'filename': "axial_slice_{}".format(axial_slider+1)}})

                    #selected_points = plotly_events(fig_axial)
                    #print(selected_points)
                    #print("cucu")
                    #state["selected_points_"].append(selected_points)
                    #if len(state["selected_points_"])>0:
                    #    print("Last chosen point is: {} {}".format(selected_points[-1]['x'], selected_points[-1]['y']))


                # figure for observation
                st.image(img_view, caption='Slice {} out of {}'.format(axial_slider+1, img3d.shape[2], width=width))

            
            if 'Coronal' in options:
                st.markdown('<h2>Coronal view</h2>', unsafe_allow_html=True)
                #coronal_slider = st.slider(
                #    'Coronal Slices',
                #    1, img3d.shape[0], (img3d.shape[0] + 1)//2
                #)-1

                col1, col2 = st.beta_columns([.5,.5])

                with col2:
                    if(st.button("Next Coronal slice")):
                        state["coronal_slice_"] = (state["coronal_slice_"] + 1) % (img3d.shape[0])
                        coronal_slice = state["coronal_slice_"]

                with col1:
                    if(st.button("Previous Coronal slice")):
                        state["coronal_slice_"] = (state["coronal_slice_"] - 1) % (img3d.shape[0])
                        coronal_slice = state["coronal_slice_"]

                coronal_max = int(img3d[coronal_slice, :, :].max())
                coronal_min = int(img3d[coronal_slice, :, :].min())
                coronal_threshold_tuple = st.slider(
                    'Coronal Color Threshold',
                    0, 100, (40, 60)
                )
                coronal_threshold = [0,0]
                coronal_threshold[0], coronal_threshold[1] = coronal_threshold_tuple
                coronal_threshold[1] = coronal_max * ((2 * coronal_threshold[1] / 100) - 1)
                coronal_threshold[0] = coronal_min * ((2 * coronal_threshold[0] / 100) - 1)
                st.image(normalize_image(filter_image2(coronal_threshold, resize(ndimage.rotate(img3d[coronal_slice, :, :].T, 180), (img3d.shape[0],img3d.shape[0])))), 
                                                            caption='Slice {} out of {}'.format(coronal_slice+1, img3d.shape[0]), width=width)

            if 'Sagittal' in options:
                st.markdown('<h2>Sagittal view</h2>', unsafe_allow_html=True)
                sagittal_slider = st.slider(
                    'Sagittal Slices',
                    1, img3d.shape[1], (img3d.shape[1] + 1)//2
                )-1
                sagittal_max = int(img3d[:, sagittal_slider, :].max())
                sagittal_min = int(img3d[:, sagittal_slider, :].min())
                sagittal_threshold_tuple = st.slider(
                    'Sagittal Color Threshold',
                    0, 100, (40, 60)
                )
                sagittal_threshold = [0,0]
                sagittal_threshold[0], sagittal_threshold[1] = sagittal_threshold_tuple
                sagittal_threshold[1] = sagittal_max * ((2 * sagittal_threshold[1] / 100) - 1)
                sagittal_threshold[0] = sagittal_min * ((2 * sagittal_threshold[0] / 100) - 1)
                st.image(normalize_image(filter_image2(sagittal_threshold, resize(ndimage.rotate(img3d[:, sagittal_slider-1, :], 90), (img3d.shape[0],img3d.shape[0])))), 
                                                            caption='Slice {} out of {}'.format(sagittal_slider+1, img3d.shape[1]), width=width)

            if options:
                st.sidebar.markdown('<h2 style=\'font-size:0.65em\'>Logging of Anomalyes</h2>', unsafe_allow_html=True)
                #st.text_area('Add new anomaly')
                new_anomaly = st.sidebar.text_input("Insert new Anomaly or select one below", value="", help="Adds a new Anomaly to the below list of Anomalies")
                anomaly = st.sidebar.selectbox('Select Anomaly', state["stored_anomalyes_"], index=0, help="Select a pre-existing Anomaly or add a new one using the field above")
                
                if new_anomaly != "" and new_anomaly not in state["stored_anomalyes_"]:
                    state["stored_anomalyes_"].append(new_anomaly)
                anomaly_slices = st.sidebar.text_input("Axial Annotation - Slices with Anomaly", value="", help="Example: 0-11; 57-59; 112;")
                
                if st.sidebar.button("Add Anomaly to log"):
                    #state[selected_serie][2]['Anomaly'] = st.sidebar.text_input('Anomaly Label', value=state[selected_serie][2]['Anomaly'])
                    state[selected_serie][2]['Anomaly'] += anomaly + " // "
                    #if 'Axial' in options:
                    state[selected_serie][2]['Slices'] += anomaly_slices + " // "

            
            #st.sidebar.markdown('<h1 style=\'font-size:0.65em\'> Example of annotation with slices: 0-11; 57-59; 112; </h1> ', unsafe_allow_html=True)


            if options:
                annotation_selected = st.sidebar.multiselect('Annotated series to be included in the .json log', series_names, series_names)
                json_selected = {serie: state[serie][2] for serie in annotation_selected}
                
                if st.checkbox('Check Annotations.json', value=True):
                    st.write(json_selected)
                
                download_button_str = download_button(json_selected, 'Annotation.json', 'Download Annotation.json')
                st.sidebar.markdown(download_button_str, unsafe_allow_html=True) 

        del img3d, info

    if st.sidebar.checkbox('Notes', value=True):
        st.sidebar.markdown('1. It does not recognize .zip archives inside other .zip archives.')
        st.sidebar.markdown('2. It only recognizes series with two or more .dcm files.')
        st.sidebar.markdown('3. You can use the arrow keys to change the slider widgets.')
        st.sidebar.markdown('4. Uploaded files are cached until the heroku server session becomes idle (30 min).'
                            ' Then, they are automatically deleted.')
    
    gc.collect()
    state.sync()