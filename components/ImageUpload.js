import React, { useState } from 'react'

const ImageUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [extractedText, setExtractedText] = useState('')

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    setSelectedFile(file)
    setExtractedText('')
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch('http://localhost:8000/ocr', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        setExtractedText(result.text || 'No text extracted')
      } else {
        setExtractedText('Failed to extract text from image')
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      setExtractedText('Error occurred during upload')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="image-upload">
      <div className="upload-section">
        <label htmlFor="file-input" className="file-label">
          {selectedFile ? selectedFile.name : 'Select medical document or image'}
        </label>
        <input 
          id="file-input"
          type="file" 
          onChange={handleFileSelect} 
          accept="image/*,.pdf" 
          style={{ display: 'none' }}
        />
        {selectedFile && (
          <button 
            onClick={handleUpload} 
            disabled={isUploading}
            className="upload-button"
          >
            {isUploading ? 'Processing...' : 'Extract Text'}
          </button>
        )}
      </div>
      
      {extractedText && (
        <div className="extracted-text">
          <h4>Extracted Text:</h4>
          <div className="text-content">{extractedText}</div>
        </div>
      )}
    </div>
  )
}

export default ImageUpload
