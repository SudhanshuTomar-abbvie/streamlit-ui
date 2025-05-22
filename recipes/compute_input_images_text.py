import os
import pandas as pd
import dataiku
from PIL import Image
import pytesseract
import re

class ImageTextExtractor:
    """
    A class to extract text from images stored in a Dataiku managed folder
    and write the results to a Dataiku dataset using a DataFrame.
    Only images with extracted text containing more than 5 words are included.
    """
    
    def __init__(self, input_folder_name, output_dataset_name):
        """
        Initialize the extractor with input folder and output dataset names.
        
        Args:
            input_folder_name: Name of the Dataiku managed folder containing images
            output_dataset_name: Name of the Dataiku dataset to write results to
        """
        self.input_folder = dataiku.Folder(input_folder_name)
        self.output_dataset = dataiku.Dataset(output_dataset_name)
        
    def extract_text_from_image(self, image_path):
        """
        Extract text from a single image using pytesseract OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string with cleaned whitespace
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            
            # Clean up the extracted text
            # Replace multiple whitespaces with a single space
            cleaned_text = re.sub(r'\s+', ' ', text)
            # Remove leading and trailing whitespace
            cleaned_text = cleaned_text.strip()
            
            return cleaned_text
        except Exception as e:
            print(f"Error extracting text from {image_path}: {str(e)}")
            return ""
    
    def process_all_images(self):
        """
        Process all images in the input folder and create a DataFrame with the results.
        Only include images with more than 5 words in the extracted text.
        Then write the DataFrame to the output dataset.
        """
        # Get list of files in the managed folder
        file_list = self.input_folder.list_paths_in_partition()
        
        # Prepare data for DataFrame
        image_names = []
        extracted_texts = []
        
        # Track statistics
        total_images = 0
        included_images = 0
        
        # Process each image file
        for file_path in file_list:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                total_images += 1
                # Get the image name from the path
                image_name = os.path.basename(file_path)
                
                # Get the full path for the file in the managed folder
                with self.input_folder.get_download_stream(file_path) as stream:
                    # Save temporarily
                    temp_path = f"/tmp/{image_name}"
                    with open(temp_path, 'wb') as f:
                        f.write(stream.read())
                    
                    # Extract text
                    extracted_text = self.extract_text_from_image(temp_path)
                    
                    # Clean up
                    os.remove(temp_path)
                
                # Check if extracted text has more than 5 words
                word_count = len(extracted_text.split())
                if word_count > 5:
                    # Append to lists
                    image_names.append(image_name)
                    extracted_texts.append(extracted_text)
                    included_images += 1
                    print(f"Processed {image_name} - {word_count} words - INCLUDED")
                else:
                    print(f"Processed {image_name} - {word_count} words - SKIPPED (less than 5 words)")
        
        # Create DataFrame
        results_df = pd.DataFrame({
            "image_name": image_names,
            "extracted_text": extracted_texts,
            "word_count": [len(text.split()) for text in extracted_texts]
        })
        
        # Write DataFrame to output dataset
        self.output_dataset.write_with_schema(results_df)
        
        print(f"Total images processed: {total_images}")
        print(f"Images included in dataset: {included_images}")
        print(f"Images excluded (less than 5 words): {total_images - included_images}")
        
        return results_df

# Example usage:
def main():
    # Replace with your actual folder and dataset names
    extractor = ImageTextExtractor(
        input_folder_name="input_images_extracted_custom",
        output_dataset_name="input_images_text"
    )
    
    df = extractor.process_all_images()
    print(f"Text extraction completed! Added {len(df)} images to dataset.")

if __name__ == "__main__":
    main()