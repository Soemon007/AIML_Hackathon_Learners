from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pathlib import Path
import re
import os
from datetime import datetime

IMG_DIR = "assets"
images = ["sedex.png","iso 9001.png"]

def apply_formatting_to_placeholder(placeholder, text):
    text_frame = placeholder.text_frame
    text_frame.clear()
    
    p = text_frame.paragraphs[0] if text_frame.paragraphs else text_frame.add_paragraph()
    
    parts = re.split(r'\*\*(.*?)\*\*', text)
    
    for i, part in enumerate(parts):
        if part: 
            run = p.add_run()
            run.text = part
            run.font.bold = (i % 2 == 1)

def create_ppt(slides_data):
  # slides_data is now a Dictionary, not a massive string.
  
  def add_slide_from_template(prs, layout_index, placeholder_text = None, placeholder_charts = None, placeholder_images = None):
      slide = prs.slides.add_slide(prs.slide_layouts[layout_index])
     
      if placeholder_text:
          for idx, text_val in placeholder_text.items():
              # Handle list of bullets -> String with newlines
              if isinstance(text_val, list):
                  final_text = "\n".join(text_val)
              else:
                  final_text = str(text_val)
                  
              try:
                 apply_formatting_to_placeholder(slide.placeholders[idx], final_text)
              except KeyError:
                 print(f"⚠️ Placeholder {idx} not found on slide layout {layout_index}")

      if placeholder_charts:
        for idx, (chart_type, chart_data) in placeholder_charts.items():
            if not chart_data: continue

            try:
                placeholder = slide.placeholders[idx]
            except KeyError:
                print(f"⚠️ Placeholder {idx} not found for chart.")
                continue

            # Capture dimensions
            x, y, cx, cy = placeholder.left, placeholder.top, placeholder.width, placeholder.height

            # Delete placeholder to prevent "Add Chart" text
            sp = placeholder.element
            sp.getparent().remove(sp)

            # Create the New Chart
            graphic_frame = slide.shapes.add_chart(
                chart_type, x, y, cx, cy, chart_data
            )
            chart = graphic_frame.chart

            # --- FORMATTING ---
            # 1. Add Legend
            chart.has_legend = True
            chart.legend.include_in_layout = False 

            # 2. Add Data Labels
            plot = chart.plots[0]
            plot.has_data_labels = True
            data_labels = plot.data_labels
            
            # Specific formatting based on chart type
            if chart_type == XL_CHART_TYPE.PIE:
                chart.has_title = True
                chart.chart_title.text_frame.text = slides_data.get("pie_chart_data", {}).get("title", "Revenue Share")
                # Move title up
                chart.chart_title.include_in_layout = False
                
                data_labels.show_category_name = True # Shows "Revenue", "Cost", etc.
                data_labels.show_value = True         # Shows "100", "50", etc.
                data_labels.show_percentage = False   # Set to True if you want %
                data_labels.position = XL_LABEL_POSITION.BEST_FIT
            
            elif chart_type == XL_CHART_TYPE.COLUMN_CLUSTERED:
                data_labels.show_value = True # Usually just value is enough for bars
      if placeholder_images:
          for idx, image_path in placeholder_images.items():
              # 1. Skip if no path provided
              if not image_path: continue

              # 2. Skip if file doesn't exist (prevents crash)
              if not os.path.exists(image_path):
                  print(f"⚠️ Image not found: {image_path}")
                  continue

              # 3. Insert the picture
              try:
                  placeholder = slide.placeholders[idx]
                  placeholder.insert_picture(image_path)
              except:# AttributeError: CAN THIS GIVE AN ISSUE??
                 # print(f"❌ Error: Placeholder {idx} does not support images.")
                 pass


      return slide



  def delete_slide(prs, slide_index):
      slide_id_list = prs.slides._sldIdLst
      slides = list(slide_id_list)

      prs.part.drop_rel(slides[slide_index].rId)
      slide_id_list.remove(slides[slide_index])


  bar_data = CategoryChartData()
  pie_data = CategoryChartData()


  # --- PARSE PIE CHART DATA ---
  pie_data_obj = slides_data.get("pie_chart_data", {})
  # Default fallback if empty or missing
  if not pie_data_obj:
      pie_data_obj = {"title": "Default Pie", "categories": ["A", "B"], "values": [50, 50]}
      
  pie_title = pie_data_obj.get("title", "Default Pie")
  pie_cats = pie_data_obj.get("categories", [])
  pie_vals = pie_data_obj.get("values", [])

  # Ensure equal length
  min_len = min(len(pie_cats), len(pie_vals))
  pie_data.categories = pie_cats[:min_len]
  pie_data.add_series(pie_title, pie_vals[:min_len])
  
  # --- PARSE BAR CHART DATA ---
  bar_data_obj = slides_data.get("bar_chart_data", {})
  # Default fallback
  if not bar_data_obj:
      bar_data_obj = {"title": "Default Bar", "categories": ["A", "B"], "values": [50, 50]}

  bar_title = bar_data_obj.get("title", "Default Bar")
  bar_cats = bar_data_obj.get("categories", [])
  bar_vals = bar_data_obj.get("values", [])

  min_len_bar = min(len(bar_cats), len(bar_vals))
  bar_data.categories = bar_cats[:min_len_bar]
  bar_data.add_series(bar_title, bar_vals[:min_len_bar])

  prs = Presentation("Layout (1).pptx")

  # --- CERTIFICATIONS ---
  cert_raw = slides_data.get("certifications", "")
  cert = cert_raw.split("||")
  while(len(cert)<3):
    cert.append("") # Fill empty spots
    
  # Clean up filenames
  cert = [c.strip() for c in cert]

  # --- SECTOR SWITCHING LOGIC ---
  # --- SECTOR SWITCHING LOGIC ---
  sector = slides_data.get("sector", "B2B") 
  
  # New Sectors: "Consumer" maps to D2C layout. 
  # "Manufacturing", "Tech", "Pharma", "Logistics" map to B2B layout.
  # We keep "D2C" in the list for backward compatibility.
  d2c_sectors = ["D2C", "Consumer"]
  is_d2c_layout = (sector in d2c_sectors)
  
  if is_d2c_layout:
      profile_layout_idx = 5
      financials_layout_idx = 6
  else:
      # Default for B2B, Manufacturing, Tech, Pharma, Logistics
      profile_layout_idx = 1
      financials_layout_idx = 2
      
  # Unified Text Selection: prefer business_overview, fallback to brand_overview
  overview_text = slides_data.get("business_overview") or slides_data.get("brand_overview", "")

  add_slide_from_template(prs,0) #Title Slide
  add_slide_from_template(
      prs,
      layout_index=profile_layout_idx,
      placeholder_text={
         10: overview_text,
         11: slides_data.get("portfolio_and_products", ""),
         15: slides_data.get("at_a_glance", "")
      },
      placeholder_images={
        12: os.path.join(IMG_DIR, cert[0]), 
        13: os.path.join(IMG_DIR, cert[1]), 
        14: os.path.join(IMG_DIR, cert[2]) 
      }
  )
  
  add_slide_from_template(prs,
      layout_index=financials_layout_idx,
      placeholder_text={
        12: slides_data.get("bar_chart_text", ""),
        13: slides_data.get("pie_chart_text", ""),
      },
    placeholder_charts={
       10: (XL_CHART_TYPE.COLUMN_CLUSTERED, bar_data),
       11: (XL_CHART_TYPE.PIE, pie_data)
    }
      
  )
  
  # Investment Highlights
  highlights = slides_data.get("investment_highlights", [])
  # Pad with empty strings if fewer than 6
  while len(highlights) < 6:
      highlights.append("")

  add_slide_from_template(prs,
      layout_index=3,
      placeholder_text={
          10: highlights[0],
          11: highlights[1],
          12: highlights[2],
          13: highlights[3],
          14: highlights[4],
          15: highlights[5]
      }
  )

  add_slide_from_template(prs,4) #Disclaimer Slide
  delete_slide(prs, 0) #Deletes the default Slide master slide

 # Generate timestamp string: YearMonthDay_HourMinuteSecond
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create dynamic filename
  output_filename = f"output/ppt/company_{timestamp}.pptx"
    
  print(f"💾 Saving presentation to: {output_filename}")
  prs.save(output_filename)

