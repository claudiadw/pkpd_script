library(shiny)
library(rdrop2)
library(dplyr)
library(prodlim)
### FIELDS AND DIRECTORIES

fieldsAll <- c("drug_name", "pubmed_id", "paper_name", "paper_category", 
               "species", "study_arm", "number_of_subjects", "number_of_samples",
               'age','age_units','weight','weight_units','admin_r','dose',
               'dose_units','auc','auc_units','clearance_ct','clearance_units')

appDir<- "app"

# Load a pre-existing file to know the list of possible PMIDs

pmid_title <- structure(drop_read_csv("/app/entries_amoxicillin.csv",dest=tempdir()),class='data.frame')
Sys.setenv(LANG = "en_GB.UTF-8")

# FUNCTION TO LOAD DATA DEPENDING ON THE PASSWORD ENTERED

get_data <- function(passw){
  switch(passw,
         "claudia"={g_d <- drop_read_csv("/app/entries_amoxicillin_claudia.csv",dest=tempdir())},
         "ferran"={g_d <- drop_read_csv("/app/entries_amoxicillin_ferran.csv",dest=tempdir())},
         "frank"={g_d <- drop_read_csv("/app/entries_amoxicillin_frank.csv",dest=tempdir())},
         "joe"={g_d <- drop_read_csv("/app/entries_amoxicillin_joe.csv",dest=tempdir())}
  ) 
  g_d
}
# FUNCTION THAT DEFINES THE NAME OF THE FIELD SAVED DEPENDING ON PASSWORD

o_file <- function(passw){
  switch(passw,
         "claudia"={fPA <- "entries_amoxicillin_claudia.csv"},
         "ferran"={fPA <- "entries_amoxicillin_ferran.csv"},
         "frank"={fPA <- "entries_amoxicillin_frank.csv"},
         "joe"={fPA <- "entries_amoxicillin_joe.csv"}
  )  
  fPA 
}

# FUNCTION TO DELETE A ROW IN THE DATABASE ACCORDING TO PMID AND STUDY ARM 

delete_data_f <- function(pmid_d,arm_d,passw_d){
  good_data_d <- get_data(passw_d)
  new_pmid_arm_d <- c(pmid_d,arm_d)
  
  all_pmids_arms_d <- t(rbind(good_data_d$pubmed_id,good_data_d$study_arm)) 
  coordinates_d<-row.match(new_pmid_arm_d,all_pmids_arms_d)
  ifelse (is.na(coordinates_d),# Does this pmid and arm already exist?
          { # ..if they don't exist show message
            shinyjs::show("non_match_message")
            shinyjs::delay(5000,shinyjs::hide("non_match_message")) # show message during just 5sec
            #shinyjs::hide("non_match_message",anim=FALSE,animType="slide",time=3)
            print("Hey")
            
          },
          { # ..if they already exist then delete it
            good_data_d <- good_data_d[-coordinates_d,]
            filePathApp<-o_file(passw_d)
            write.csv(good_data_d,filePathApp,row.names=FALSE,quote=TRUE,fileEncoding = "UTF-8")
            drop_upload(filePathApp,path=appDir,mode="overwrite")
            shinyjs::hide("delete_data")
            shinyjs::show("delete_message")
            print("Ho")
            #shinyjs:show("gobackthree")
          })
}

# Save Data

saveData <- function(data,pmid,arm,passw) {
  
  good_data <- get_data(passw) # Generate good_data file
  data <- t(data) # Transpose to column vector
  
  #### Check if that PMID and STUDY ARM are already in the database. If not, then we just concatenate the new entry, otherwise replace it
  # Generate 2-D vectors with the pmids and arms of the old and new entries
  new_pmid_arm <- c(pmid,arm)
  all_pmids_arms <- t(rbind(good_data$pubmed_id,good_data$study_arm))  
  coordinates=row.match(new_pmid_arm,all_pmids_arms) #Check if the pmid and arm of the new entry already exists in the dataset, and if so, save the coordinates and make a replacement. 
  ifelse (is.na(coordinates),{good_data <- rbind(good_data,data)},
          {good_data <- good_data[-coordinates,] 
          good_data <- rbind(good_data,data)})
  filePathApp<-o_file(passw)
  write.csv(good_data,filePathApp,row.names=FALSE,quote=TRUE,fileEncoding = "UTF-8")
  drop_upload(filePathApp,path=appDir,mode="overwrite")
  
}

#################UI####################

ui <- fluidPage(
  
  shinyjs::useShinyjs(),
  # TITLE 
  title = "Input for PK/PD data",
  div(id = "header",
      h1("Input for PK/PD data"), h1()),
  
  #####PASSWORD AREA
  
  fluidRow(column(
    10, offset = 0,
    div(id="login",style='width:100%; display:table',
        
        passwordInput("password", "Password:"),
        actionButton("go", "Go", class="btn-primary")   
    )
  )),
  ##### END PASSWORD AREA
  ##### BEGINNING MAIN BODY ("FORM")
  
  shinyjs::hidden(fluidRow(id='form',column(
    10, offset = 100,
    div(      
      div(
        style = "display: table-cell; font-size: 15px; padding-right: 7px; margin:0%",
        
        selectizeInput("pubmed_id", choices = pmid_title$pmid, selected = NULL, label = 'PMID:'),
        selectizeInput("paper_name", choices = NULL, label = 'Paper title:'),
        textInput('study_arm','Study arm:', value = '1'),
        textInput("drug_name", "Drug Name:"),
        selectInput("paper_category","Paper type:",
                    c("Not relevant", "Modelling", "Non-compartmental")),
        textInput('species','Species:')        
      ),      
      div(
        style = "display: table-cell; font-size: 15px; padding-right: 7px ; padding-left: 7px; margin:0%",
        
        textInput("number_of_subjects","Number of subjects:"),
        textInput('number_of_samples','Total number of samples:'),
        textInput("age", "Age (central tendency measure):"),
        textInput('age_units', 'Age units:'),
        textInput("weight", "Weight (central tendency measure):"),
        textInput('weight_units','Weight units:'),
        textInput("admin_r", "Route of administration:")
        
      ),   
      div(
        style = "display: table-cell; font-size: 15px; padding-right: 7px ; padding-left: 7px; margin:0%",      
        textInput('dose','Dose:'),
        textInput('dose_units','Dose units:'),
        textInput('auc','AUC:'),
        textInput('auc_units','AUC units:'),
        textInput("clearance_ct","Clearance (central tendency measure):"),
        textInput("clearance_units","Clearance units:"),
        div( 
          style = "display: table-cell; font-size: 15px; float: right ; padding-top: 24px; margin:0%",
          
          actionButton("submit", "Submit", class = "btn-primary")),
        
        div( style = "display: table-cell; font-size: 15px; float: right ; padding-top: 24px;padding-right:7px; margin:0%",
             actionButton("logout", "Log Out", class = "btn-primary")
        ),
        div( style = "display: table-cell; font-size: 15px; float: right ; padding-top: 24px;padding-right:7px; margin:0%",
             actionButton("view", "View my dataset", class = "btn-primary")
        ),
        div( style = "display: table-cell; font-size: 15px; float: right ; padding-top: 24px;padding-right:7px; margin:0%",
             actionButton("delete_from_main", "Delete entry", class = "btn-primary")
        )
        
      ),      
      div(
        style = "visibility: collapse;",
        DT::dataTableOutput('firstTab')
      ),
      
      shinyjs::hidden(span(id = "submit_msg", "Submitting..."),
                      div(id = "error",
                          div(
                            br(), tags$b("Error: "), span(id = "error_msg")
                          )))
    )
  ))
  ), 
  ##### END OF THE MAIN BODY FORM  
  ##### PANELS' DELETION
  
  shinyjs::hidden(
    div (id = "delete_data",style='width:100%; display:table',
         div(style = "display: table-cell; font-size: 15px; float: right ; padding-top: 15px;padding-right:2000px; margin:0%",
             selectizeInput("pubmed_id_d", choices = pmid_title$pmid, selected = NULL, label = 'PMID:')),
         div(style = "display: table-cell; font-size: 15px; float: right ; padding-top: 15px;padding-right:2000px; margin:0%",
             textInput('study_arm_d','Study arm:', value = '1')),
         div(style = "display: table-cell; font-size: 15px; float: right ; padding-top: 15px;padding-right:2235px; margin:0%",
             actionButton('delete_entry','Delete', class = "btn-primary")),
         div( style = "display: table-cell; font-size: 15px; float: right ; padding-top: 15px;padding-right:2220px; margin:0%",
              actionButton("goback", "Go Back", class = "btn-primary"))
    )
  ),# Main deletion panel
  
  shinyjs::hidden(div(
    id = "non_match_message",
    column(6,h3(style="color:red","None matching element")))
    
  ),# Display when trying to delete an entry that doesn't exist
  
  shinyjs::hidden(div(
    id = "delete_message",
    column(6,h3(style="color:green","Entry successfully deleted!")),
    div( style = "display: table-cell; font-size: 15px; float: right ;   border-collapse: separate;border-spacing: 10px;width: 100%",
         actionButton("delete_other", "Delete another entry", class = "btn-primary")),
    div( style = "display: table-cell; font-size: 15px; float: right ; padding-top:5px;   border-collapse: separate;border-spacing: 10px;width: 100%",
         actionButton("goback_three", "Go Back", class = "btn-primary")))
  ), # Display when deletion has been successful
  
  ##### END PANELS DELETION
  
  shinyjs::hidden(div(
    id = "thankyou_msg",
    column(6,h3("SUBMITTED"),actionLink("submit_another", "Submit another response")))
    
  ), # PANEL TO DISPLAY WHEN SUBMISSION IS SUCCESSFUL
  
  ##### VISUALIZE DATA PANEL
  shinyjs::hidden(div(id = "vis_data",
                      style='width:100%; display:table',
                      div(style = "display: table-cell; font-size: 15px; float: right ; padding-top: 15px;padding-right:2225px; margin:0%",
                          downloadButton(outputId = "download_data", label = "Download my data")),
                      div( style = "display: table-cell; font-size: 15px; float: right ; padding-top: 15px;padding-right:2225px; margin:0%",
                           actionButton("goback_t", "Go Back", class = "btn-primary")),
                      div(style = "display: table-cell; font-size: 15px; float: right ; padding-top: 50px;padding-right:7px; margin:0%",
                          DT::dataTableOutput(outputId = "pkpdtable"))
  )
  )
)


#################SERVER####################

server <- function(input, output, session) {
  
  # After introducing the right password go to the main UI and load the specific dataset (c/j/fe/fr)
  
  observeEvent(input$go, {
    
    if (input$password == "claudia"||input$password == "ferran"||input$password == "joe"||input$password == "frank")
    {shinyjs::hide('go')
      shinyjs::hide('password')
      shinyjs::show('form') 
      shinyjs::hide("vis_data")
      shinyjs::hide("thankyou_msg")
    }
  }
  )
  # Assign title to the selected PMID
  updateApp <- reactive({
    data <- pmid_title
    data <- data[data$pmid %in% input$pubmed_id,]
    updateSelectizeInput(session, 'paper_name', choices = data$title, selected = data$title, server = TRUE)
    data
  })
  # Update title table  
  output$firstTab <- DT::renderDataTable(
    DT::datatable(updateApp()) 
  )
  # Generate new row according to the inputs given in the UI
  formData <- reactive({
    data <- sapply(fieldsAll, function(x)
      input[[x]])
    data
  })
  
  # Logout button
  
  observeEvent(input$logout, {
    shinyjs::reset("password")
    shinyjs::reset("form")
    shinyjs::show("password")
    shinyjs::show("go") 
    shinyjs::hide("form")  
  })
  # View Data button
  observeEvent(input$view, { 
    shinyjs::reset("vis_data")
    shinyjs::hide("form")
    shinyjs::show("vis_data")
  })
  # Go-back from view
  
  observeEvent(input$goback_t, {   
    shinyjs::hide("vis_data")
    shinyjs::show("form")     
  })
  
  # Go-back from delete data
  observeEvent(input$goback, {   
    shinyjs::hide("delete_data")
    shinyjs::show("form")
    shinyjs::reset("vis_data")
  })
  
  # Go-back from delete_message
  
  observeEvent(input$goback_three, { 
    shinyjs::hide("delete_message")
    shinyjs::show("form") 
    shinyjs::reset("vis_data")
  })
  # Delete other from delete_message
  observeEvent(input$delete_other, {
    shinyjs::hide("delete_message")
    shinyjs::show("delete_data")
  })
  
  # Submit button (Here is where everything is done)
  observeEvent(input$submit, {
    
    shinyjs::disable("submit")
    shinyjs::disable("view")
    shinyjs::disable("logout")
    shinyjs::disable("delete_from_main")
    shinyjs::show("submit_msg")
    shinyjs::hide("error")
    shinyjs::reset("vis_data")
    shinyjs::hide("vis_data")
    # Save the data (show an error message in case of error)
    tryCatch({
      
      saveData(formData(),input$pubmed_id,input$study_arm ,input$password)
      shinyjs::reset("form")
      shinyjs::hide("form")
      shinyjs::show("thankyou_msg")
    },
    
    
    error = function(err) {
      shinyjs::html("error_msg", err$message)
      shinyjs::show(id = "error",
                    anim = TRUE,
                    animType = "fade")
      shinyjs::hide("form")
    },
    finally = {
      shinyjs::enable("submit")
      shinyjs::hide("submit_msg")
    })
    shinyjs::enable("submit")
    shinyjs::enable("view")
    shinyjs::enable("logout")
    shinyjs::enable("delete_from_main")
  })
  
  #Delete entry from delete_data
  observeEvent(input$delete_entry,
               { shinyjs::disable("delete_entry")
                 shinyjs::disable("goback")
                 shinyjs::reset("vis_data")
                 shinyjs::hide("vis_data")
                 delete_data_f(input$pubmed_id_d,input$study_arm_d,input$password)
                 shinyjs::enable("delete_entry")
                 shinyjs::enable("goback")
                 
                 #shinyjs::show("delete_message")
                 #shinyjs::hide("delete_data")
               })
  # Submit another response button
  observeEvent(input$submit_another, {
    shinyjs::show("form")
    shinyjs::hide("thankyou_msg")
  })
  # Download file
  output$download_data <- downloadHandler(
    filename = function(){ paste("data-", Sys.Date(), ".csv", sep="")}, 
    content = function(file) {write.csv(get_data(input$password),file)} ,contentType="csv"
  )
  
  # Buttom to go from main to delete panel
  observeEvent(input$delete_from_main,{
    shinyjs::hide("form")
    shinyjs::show("delete_data")
  })
  
  # Create data table 
  output$pkpdtable <- DT::renderDataTable({
    all_data <- get_data(input$password)
    ss=nrow(all_data)
    papers_sample <- all_data %>%
      sample_n(ss) %>%
      select(drug_name:clearance_units)
    DT::datatable(data = all_data, 
                  options = list(pageLength = 20), 
                  rownames = FALSE)
    
  })
  
}

#################SPECIFY THAT THIS IS AN APP###############

shinyApp(ui=ui,server=server)
