/**
 * S-02 Upload Page — Upload Zone A/B/C documents and start a new pipeline run.
 */
import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { runsApi } from '../../services/api'
import toast from 'react-hot-toast'

type Zone = 'zone_a' | 'zone_b' | 'zone_c'

const MAX_FILE_MB = 100
const MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024

const ZONE_INFO: Record<Zone, { label: string; description: string; accept: string; icon: string; required: boolean }> = {
  zone_a: {
    label:       'Zone A — Source Documents',
    description: 'Clinical trial source documents: protocols, SAP, patient narratives, CRFs',
    accept:      '.pdf',
    icon:        '📄',
    required:    true,
  },
  zone_b: {
    label:       'Zone B — TFL Output',
    description: 'Tables, Figures and Listings (TFLs) from statistical analysis',
    accept:      '.pdf,.xlsx,.xls',
    icon:        '📊',
    required:    true,
  },
  zone_c: {
    label:       'Zone C — Compliance Guidelines',
    description: 'ICH E3, ICH E6, FDA formatting guidelines',
    accept:      '.pdf',
    icon:        '📏',
    required:    true,
  },
}

interface FileDropZoneProps {
  zone: Zone
  files: File[]
  onFiles: (zone: Zone, files: File[]) => void
}

function FileDropZone({ zone, files, onFiles }: FileDropZoneProps) {
  const info = ZONE_INFO[zone]
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const dropped = Array.from(e.dataTransfer.files)
    onFiles(zone, dropped)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      onFiles(zone, Array.from(e.target.files))
    }
  }

  const removeFile = (idx: number) => {
    const updated = files.filter((_, i) => i !== idx)
    onFiles(zone, updated)
  }

  return (
    <div className={`card p-5 ${info.required ? 'border-l-4 border-l-brand-400' : ''}`}>
      <div className="flex items-start gap-3 mb-3">
        <span className="text-2xl">{info.icon}</span>
        <div>
          <h3 className="font-semibold text-gray-800 text-sm">
            {info.label}
            {info.required && <span className="text-red-500 ml-1">*</span>}
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">{info.description}</p>
          <p className="text-xs text-gray-400 mt-1">Accepted: {info.accept} · Max {MAX_FILE_MB} MB per file</p>
        </div>
      </div>

      {/* Drop area */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
          dragging ? 'border-brand-500 bg-brand-50' : 'border-gray-300 hover:border-brand-400 hover:bg-gray-50'
        }`}
      >
        <p className="text-sm text-gray-500">
          {dragging ? 'Drop files here' : 'Drag & drop or click to browse'}
        </p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={info.accept}
          className="hidden"
          onChange={handleFileInput}
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <ul className="mt-3 space-y-1.5">
          {files.map((f, idx) => (
            <li key={idx} className="flex items-center justify-between text-xs bg-gray-50 px-3 py-1.5 rounded-lg">
              <span className="truncate text-gray-700">{f.name}</span>
              <span className="text-gray-400 ml-2 flex-shrink-0">
                {(f.size / 1024 / 1024).toFixed(1)} MB
              </span>
              <button
                onClick={(e) => { e.stopPropagation(); removeFile(idx) }}
                className="ml-2 text-gray-400 hover:text-red-500 flex-shrink-0"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

interface ConfirmModalProps {
  runName: string
  zoneA: File[]
  zoneB: File[]
  zoneC: File[]
  onConfirm: () => void
  onCancel: () => void
}

function ConfirmModal({ runName, zoneA, zoneB, zoneC, onConfirm, onCancel }: ConfirmModalProps) {
  const totalFiles = zoneA.length + zoneB.length + zoneC.length
  const totalMB = [...zoneA, ...zoneB, ...zoneC]
    .reduce((sum, f) => sum + f.size, 0) / 1024 / 1024

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
        <h2 className="text-lg font-bold text-gray-900 mb-1">Confirm Pipeline Start</h2>
        <p className="text-sm text-gray-500 mb-5">
          Please review your submission before starting the AI pipeline.
        </p>

        <div className="space-y-3 mb-6">
          <div className="bg-gray-50 rounded-lg px-4 py-3">
            <p className="text-xs font-medium text-gray-500 mb-0.5">Run Name</p>
            <p className="text-sm font-semibold text-gray-800">{runName}</p>
          </div>

          {[
            { label: 'Zone A — Source Documents', files: zoneA },
            { label: 'Zone B — TFL Output', files: zoneB },
            { label: 'Zone C — Compliance Guidelines', files: zoneC },
          ].map(({ label, files }) => (
            <div key={label} className="bg-gray-50 rounded-lg px-4 py-3">
              <p className="text-xs font-medium text-gray-500 mb-1">{label}</p>
              <ul className="space-y-0.5">
                {files.map((f, i) => (
                  <li key={i} className="text-xs text-gray-700 flex justify-between">
                    <span className="truncate">{f.name}</span>
                    <span className="text-gray-400 ml-2 flex-shrink-0">{(f.size / 1024 / 1024).toFixed(1)} MB</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div className="text-xs text-gray-500 text-right">
            {totalFiles} file{totalFiles !== 1 ? 's' : ''} · {totalMB.toFixed(1)} MB total
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <button onClick={onCancel} className="btn-secondary">
            Cancel
          </button>
          <button onClick={onConfirm} className="btn-primary">
            🚀 Start Pipeline
          </button>
        </div>
      </div>
    </div>
  )
}

export default function UploadPage() {
  const [runName, setRunName]       = useState('')
  const [zoneA, setZoneA]           = useState<File[]>([])
  const [zoneB, setZoneB]           = useState<File[]>([])
  const [zoneC, setZoneC]           = useState<File[]>([])
  const [loading, setLoading]       = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const navigate                    = useNavigate()

  const handleZoneFiles = (zone: Zone, files: File[]) => {
    // Validate file sizes
    const oversized = files.filter((f) => f.size > MAX_FILE_BYTES)
    if (oversized.length > 0) {
      oversized.forEach((f) =>
        toast.error(`${f.name} exceeds the ${MAX_FILE_MB} MB file size limit`)
      )
      // Only keep valid files
      const valid = files.filter((f) => f.size <= MAX_FILE_BYTES)
      if (zone === 'zone_a') setZoneA(valid)
      if (zone === 'zone_b') setZoneB(valid)
      if (zone === 'zone_c') setZoneC(valid)
      return
    }
    if (zone === 'zone_a') setZoneA(files)
    if (zone === 'zone_b') setZoneB(files)
    if (zone === 'zone_c') setZoneC(files)
  }

  const handleSubmitClick = (e: React.FormEvent) => {
    e.preventDefault()
    if (!runName.trim()) {
      toast.error('Please enter a run name')
      return
    }
    if (zoneA.length === 0) {
      toast.error('Zone A (Source Documents) is required')
      return
    }
    if (zoneB.length === 0) {
      toast.error('Zone B (TFL Output) is required')
      return
    }
    if (zoneC.length === 0) {
      toast.error('Zone C (Compliance Guidelines) is required')
      return
    }
    setShowConfirm(true)
  }

  const handleConfirm = async () => {
    setShowConfirm(false)
    const formData = new FormData()
    formData.append('run_name', runName.trim())
    zoneA.forEach((f) => formData.append('zone_a_files', f))
    zoneB.forEach((f) => formData.append('zone_b_files', f))
    zoneC.forEach((f) => formData.append('zone_c_files', f))

    setLoading(true)
    try {
      const res = await runsApi.create(formData)
      toast.success('Pipeline started!')
      navigate(`/runs/${res.data.id}/pipeline`)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? 'Failed to start pipeline')
    } finally {
      setLoading(false)
    }
  }

  const totalFiles = zoneA.length + zoneB.length + zoneC.length
  const allZonesFilled = zoneA.length > 0 && zoneB.length > 0 && zoneC.length > 0

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">New CSR Run</h1>
        <p className="text-gray-500 text-sm mt-1">
          Upload your study documents and start the AI-powered CSR generation pipeline.
        </p>
      </div>

      <form onSubmit={handleSubmitClick} className="space-y-5">
        {/* Run name */}
        <div className="card p-5">
          <label className="label">Run Name *</label>
          <input
            type="text"
            className="input"
            placeholder="e.g. Study ABC-123 — Primary Analysis v1"
            value={runName}
            onChange={(e) => setRunName(e.target.value)}
            maxLength={200}
          />
          <p className="text-xs text-gray-400 mt-1">
            A descriptive name to identify this CSR generation run.
          </p>
        </div>

        {/* Zone uploads */}
        <FileDropZone zone="zone_a" files={zoneA} onFiles={handleZoneFiles} />
        <FileDropZone zone="zone_b" files={zoneB} onFiles={handleZoneFiles} />
        <FileDropZone zone="zone_c" files={zoneC} onFiles={handleZoneFiles} />

        {/* Submit */}
        <div className="flex items-center justify-between pt-2">
          <p className="text-sm text-gray-500">
            {totalFiles > 0 ? `${totalFiles} file${totalFiles !== 1 ? 's' : ''} selected` : 'No files selected'}
            {totalFiles > 0 && !allZonesFilled && (
              <span className="text-amber-500 ml-2">— all 3 zones required</span>
            )}
          </p>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !runName.trim() || !allZonesFilled}
          >
            {loading ? 'Starting...' : '🚀 Start Pipeline'}
          </button>
        </div>
      </form>

      {showConfirm && (
        <ConfirmModal
          runName={runName}
          zoneA={zoneA}
          zoneB={zoneB}
          zoneC={zoneC}
          onConfirm={handleConfirm}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </div>
  )
}
