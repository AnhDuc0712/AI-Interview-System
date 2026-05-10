import { useRef, useState } from 'react';

type CVUploadDropzoneProps = {
  disabled?: boolean;
  helperText?: string;
  error?: string | null;
  onFileSelect: (file: File) => void;
};

const CVUploadDropzone = ({
  disabled = false,
  helperText = 'PDF or DOCX up to 5MB',
  error,
  onFileSelect
}: CVUploadDropzoneProps) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) {
      return;
    }
    onFileSelect(fileList[0]);
  };

  return (
    <div
      className={`rounded-3xl border-2 border-dashed p-6 transition ${
        disabled
          ? 'cursor-not-allowed border-slate-200 bg-slate-50'
          : isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-slate-300 bg-slate-50/80 hover:border-blue-400 hover:bg-blue-50/60'
      }`}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) {
          setIsDragging(true);
        }
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        if (!disabled) {
          handleFiles(event.dataTransfer.files);
        }
      }}
    >
      <input
        ref={inputRef}
        accept=".pdf,.docx"
        className="hidden"
        disabled={disabled}
        onChange={(event) => handleFiles(event.target.files)}
        type="file"
      />
      <div className="flex flex-col items-center justify-center text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-2xl shadow-sm">
          <span>CV</span>
        </div>
        <h3 className="mt-4 text-lg font-semibold text-slate-900">Drop your CV here</h3>
        <p className="mt-2 max-w-sm text-sm text-slate-500">
          Upload your latest resume to unlock AI-ready profile parsing, CV history, and a clean workspace.
        </p>
        <button
          className="mt-5 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
          type="button"
        >
          Choose file
        </button>
        <p className="mt-3 text-xs text-slate-500">{helperText}</p>
        {error ? <p className="mt-2 text-sm font-medium text-rose-600">{error}</p> : null}
      </div>
    </div>
  );
};

export default CVUploadDropzone;
