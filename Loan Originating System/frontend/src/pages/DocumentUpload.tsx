import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertTriangle, CheckCircle, X, ArrowRight } from 'lucide-react'
import clsx from 'clsx'
import { Document } from '../types'

const DOC_TYPES = [
  { value: 'tax_return', label: 'Tax Return', desc: '2023 or 2024 business/personal tax return (PDF)' },
  { value: 'bank_statement', label: 'Bank Statement', desc: '12 months of bank statements' },
  { value: 'id', label: 'Government ID', desc: "Driver's license or passport" },
  { value: 'business_license', label: 'Business License', desc: 'State business registration / license' },
]

export default function DocumentUpload() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const [appId, setAppId] = useState<number | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedType, setSelectedType] = useState('tax_return')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (sessionId) {
      // sessionId is actually numeric appId when coming from BorrowerApplication
      setAppId(parseInt(sessionId))
      loadDocuments(parseInt(sessionId))
    }
  }, [sessionId])

  const loadDocuments = async (id: number) => {
    try {
      const res = await axios.get(`/api/documents/${id}`)
      setDocuments(res.data)
    } catch { /* ignore */ }
  }

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    multiple: false,
    accept: { 'application/pdf': [], 'image/*': [] },
  })

  const upload = async () => {
    if (!acceptedFiles[0] || !appId) return
    setUploading(true)
    setError(null)
    const fd = new FormData()
    fd.append('application_id', String(appId))
    fd.append('doc_type', selectedType)
    fd.append('file', acceptedFiles[0])
    try {
      await axios.post('/api/documents/upload', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      await loadDocuments(appId)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const remove = async (docId: number) => {
    await axios.delete(`/api/documents/${docId}`)
    setDocuments(d => d.filter(x => x.id !== docId))
  }

  const uploadedTypes = documents.map(d => d.doc_type)
  const missingDocs = DOC_TYPES.filter(t => !uploadedTypes.includes(t.value))

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Document Upload</h1>
        <p className="text-slate-400 mt-1">Upload supporting documents to strengthen your application.</p>
      </div>

      {/* Missing docs prompt */}
      {missingDocs.length > 0 && (
        <div className="mb-6 p-4 bg-amber-900/20 border border-amber-700/50 rounded-xl">
          <div className="flex items-center gap-2 text-amber-300 font-medium mb-2">
            <AlertTriangle className="w-4 h-4" />
            Documents Needed
          </div>
          <ul className="space-y-1">
            {missingDocs.map(d => (
              <li key={d.value} className="text-sm text-amber-200 flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-amber-400 rounded-full" />
                {d.label} — {d.desc}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Upload area */}
      <div className="card space-y-4 mb-6">
        <div>
          <label className="label">Document Type</label>
          <div className="grid grid-cols-2 gap-2">
            {DOC_TYPES.map(t => (
              <button
                key={t.value}
                onClick={() => setSelectedType(t.value)}
                className={clsx(
                  'p-3 rounded-lg border text-left text-sm transition-all',
                  selectedType === t.value
                    ? 'border-indigo-500 bg-indigo-600/20 text-white'
                    : 'border-slate-700 text-slate-400 hover:border-slate-600'
                )}
              >
                <div className="font-medium">{t.label}</div>
              </button>
            ))}
          </div>
        </div>

        <div
          {...getRootProps()}
          className={clsx(
            'border-2 border-dashed rounded-xl p-8 flex flex-col items-center gap-3 cursor-pointer transition-all',
            isDragActive
              ? 'border-indigo-500 bg-indigo-900/20'
              : 'border-slate-700 hover:border-slate-600'
          )}
        >
          <input {...getInputProps()} />
          <Upload className={clsx('w-8 h-8', isDragActive ? 'text-indigo-400' : 'text-slate-500')} />
          {acceptedFiles[0] ? (
            <div className="text-center">
              <div className="text-white font-medium">{acceptedFiles[0].name}</div>
              <div className="text-slate-400 text-sm">{(acceptedFiles[0].size / 1024).toFixed(0)} KB</div>
            </div>
          ) : (
            <div className="text-center">
              <div className="text-slate-300 font-medium">Drop file here or click to browse</div>
              <div className="text-slate-500 text-sm">PDF, JPG, PNG up to 20MB</div>
            </div>
          )}
        </div>

        {error && <div className="text-red-400 text-sm">{error}</div>}

        <button
          onClick={upload}
          disabled={!acceptedFiles[0] || uploading}
          className="btn-primary w-full"
        >
          {uploading ? 'Processing document…' : 'Upload Document'}
        </button>
      </div>

      {/* Uploaded Documents */}
      {documents.length > 0 && (
        <div className="card space-y-3">
          <h2 className="font-semibold text-white">Uploaded Documents</h2>
          {documents.map(doc => (
            <div
              key={doc.id}
              className="flex items-center justify-between p-3 bg-slate-800 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className={clsx(
                  'w-8 h-8 rounded-lg flex items-center justify-center',
                  doc.status === 'flagged' ? 'bg-red-900' : 'bg-emerald-900'
                )}>
                  {doc.status === 'flagged'
                    ? <AlertTriangle className="w-4 h-4 text-red-400" />
                    : <CheckCircle className="w-4 h-4 text-emerald-400" />
                  }
                </div>
                <div>
                  <div className="text-sm font-medium text-white">
                    {DOC_TYPES.find(t => t.value === doc.doc_type)?.label || doc.doc_type}
                  </div>
                  <div className="text-xs text-slate-400">{doc.filename}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className={clsx('text-xs font-medium', doc.status === 'flagged' ? 'text-red-400' : 'text-emerald-400')}>
                    {doc.status === 'flagged' ? 'Flagged' : 'Verified'}
                  </div>
                  <div className="text-xs text-slate-500">Tamper: {doc.tamper_score.toFixed(1)}%</div>
                </div>
                <button onClick={() => remove(doc.id)} className="text-slate-600 hover:text-red-400 transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}

          {/* Extracted data preview */}
          {documents[0]?.extracted_data && (
            <details className="mt-2">
              <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-400">
                View extracted data from last document
              </summary>
              <div className="mt-2 p-3 bg-slate-950 rounded-lg text-xs font-mono text-slate-400">
                {Object.entries(documents[0].extracted_data).map(([k, v]) => (
                  <div key={k} className="flex gap-2">
                    <span className="text-indigo-400">{k}:</span>
                    <span>{String(v)}</span>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}

      {/* Navigation */}
      <div className="mt-6 flex justify-between">
        <button onClick={() => navigate('/apply')} className="btn-secondary">
          Back to Application
        </button>
        <button
          onClick={() => navigate(`/apply/${appId}/status`)}
          className="btn-primary flex items-center gap-2"
        >
          Continue to Submit <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
