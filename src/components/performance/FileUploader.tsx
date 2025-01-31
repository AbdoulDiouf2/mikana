import { useCallback, useState, useEffect } from 'react';
import { useDropzone, type DropzoneOptions } from 'react-dropzone';
import { X, UploadCloud } from 'lucide-react';

interface FileWithPreview extends File {
  preview?: string;
}

interface FileUploaderProps {
    onUpload: (files: File[], module: string, isFolder: boolean) => Promise<void>;
}

interface ExtendedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    webkitdirectory?: string;
}

interface UploadRequirements {
  module: string;
  requiredFiles: string[];
  lastFilePresent?: string;
  notes?: string;
}

export function FileUploader({ onUpload }: FileUploaderProps) {
    const [module, setModule] = useState<string>("commandes");
    const [uploadMode, setUploadMode] = useState<"files" | "folder">("files");
    const [selectedFiles, setSelectedFiles] = useState<FileWithPreview[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const filesWithPreview = acceptedFiles.map(file => 
      Object.assign(file, { preview: URL.createObjectURL(file) })
    );
    setSelectedFiles(prev => [...prev, ...filesWithPreview]);
  }, []);

  const [lastFilePresent, setLastFilePresent] = useState<string | null>(null);

  const fetchLastLogisticFile = async () => {
    try {
      const response = await fetch("http://localhost:8001/api/performance/last-logistic-file");
      if (!response.ok) throw new Error("Erreur lors de la récupération du dernier fichier");
      const data = await response.json();
      setLastFilePresent(data.last_file);
    } catch (error) {
      console.error("Erreur :", error);
      setLastFilePresent(null);
    }
  };
  
  // Ajouter cette constante avec les informations pour chaque module
  const UPLOAD_REQUIREMENTS: UploadRequirements[] = [
    {
      module: "commandes",
      requiredFiles: ["Fichiers logistiques mensuels"],
      lastFilePresent: "logistique_2023_09.csv", // Exemple de dernier fichier présent
      notes: "Les fichiers doivent être au format Excel."
    },
    {
      module: "livraisons",
      requiredFiles: ["Planif livraisons.xlsx"],
      notes: "Le fichier doit être à jour."
    },
    {
      module: "rh",
      requiredFiles: [`PRESENCE_${new Date().getFullYear()}.xlsx`],
      notes: "Le fichier doit contenir les présences de l'année en cours."
    }
  ];

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: uploadMode === "files",
    noClick: false
  });

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    setIsUploading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("module", module);
    formData.append("is_folder", uploadMode === "folder" ? "true" : "false");
    
    selectedFiles.forEach(file => {
      formData.append("files", file);
      const path = uploadMode === 'folder' ? file.webkitRelativePath : file.name;
      formData.append("paths", path);
    });
  
    try {
      const response = await fetch("http://localhost:8001/api/performance/upload", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de l\'upload');
      }
  
      const result = await response.json();
      console.log('Upload réussi:', result);
      
      // Vider la sélection et afficher le succès
      setSelectedFiles([]);
      setSuccess(`${result.message}`);
      
      // Appeler onUpload pour mettre à jour l'interface
      await onUpload(selectedFiles, module, uploadMode === "folder");
  
    } catch (error) {
      console.error('Erreur:', error);
      setError(error instanceof Error ? error.message : 'Erreur lors de l\'upload');
    } finally {
      setIsUploading(false);
    }
  };

  const inputProps: ExtendedInputProps = {
    ...getInputProps(),
    webkitdirectory: uploadMode === 'folder' ? 'true' : undefined
  };

  useEffect(() => {
    if (module === "commandes") {
      fetchLastLogisticFile();
    } else {
      setLastFilePresent(null); // Réinitialiser si on change de module
    }
  }, [module]);

  return (
    <div className="space-y-6">
      {/* Sélection du module */}
      <div className="flex flex-wrap gap-3">
        {['commandes', 'livraisons', 'rh'].map((m) => (
          <button
            key={m}
            onClick={() => setModule(m)}
            className={`px-4 py-2 rounded-lg capitalize ${
              module === m ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      {/* Informations sur les fichiers requis */}
      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <h3 className="font-semibold mb-3">Critères d'upload</h3>
        
        {UPLOAD_REQUIREMENTS
          .filter(req => req.module === module)
          .map((req, index) => (
            <div key={index} className="space-y-2">
              <div>
                <span className="font-medium">Fichiers requis :</span>
                <ul className="list-disc list-inside">
                  {req.requiredFiles.map((file, i) => (
                    <li key={i}>{file}</li>
                  ))}
                </ul>
              </div>
              
              {module === "commandes" && (
                <div>
                  <span className="font-medium">Dernier fichier présent :</span>
                  <div className="text-sm text-gray-600">
                    {lastFilePresent || "Aucun fichier trouvé"}
                  </div>
                </div>
              )}
              
              {req.notes && (
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Note :</span> {req.notes}
                </div>
              )}
            </div>
          ))}
      </div>

      {/* Mode d'upload */}
      <div className="flex gap-3">
        {['files'].map((mode) => ( // Ne garder que 'files' dans le tableau
          <button
            key={mode}
            onClick={() => setUploadMode(mode as "files" | "folder")}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
              uploadMode === mode 
                ? 'bg-teal-500 text-white' 
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            <UploadCloud className="w-4 h-4" />
            {mode === 'files' ? 'Fichiers' : 'Dossier'}
          </button>
        ))}
        
        {/* Ajouter le bouton dossier désactivé */}
        <button
          className="px-4 py-2 rounded-lg flex items-center gap-2 bg-gray-200 text-gray-400 cursor-not-allowed relative"
          title="Non disponible - Fonctionnalité désactivée"
          disabled
        >
          <UploadCloud className="w-4 h-4" />
          Dossier
          <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-gray-700 text-white text-xs px-2 py-1 rounded opacity-0 hover:opacity-100 transition-opacity">
            Non disponible
          </div>
        </button>
      </div>

      {/* Zone de dépôt */}
      <div 
            {...getRootProps()}
            className={`p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
            >
            <input {...inputProps} />
            <div className="space-y-2">
            <UploadCloud className="mx-auto h-12 w-12 text-gray-400" />
            <p className="text-lg font-medium text-gray-900">
                {isDragActive ? 'Déposez vos fichiers ici' : 'Glissez-déposez ou cliquez pour sélectionner'}
            </p>
            <p className="text-sm text-gray-500">
                {uploadMode === 'folder' 
                ? 'Sélectionnez un dossier entier' 
                : 'Fichiers CSV/Excel uniquement'}
            </p>
        </div>
      </div>

      {/* Messages d'état */}
      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}
      
      {success && (
        <div className="p-4 bg-green-100 text-green-700 rounded-lg">
          {success}
        </div>
      )}
      

      {/* Liste des fichiers */}
      {selectedFiles.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">
              {selectedFiles.length} fichier{selectedFiles.length > 1 ? 's' : ''} sélectionné{selectedFiles.length > 1 ? 's' : ''}
            </h3>
            <button
              onClick={() => setSelectedFiles([])}
              className="text-red-500 hover:text-red-700 text-sm"
            >
              Tout effacer
            </button>
          </div>
          
          <div className="grid gap-2 max-h-60 overflow-y-auto">
            {selectedFiles.map((file, index) => (
              <div 
                key={`${file.name}-${index}`}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3 truncate">
                  <span className="font-mono text-sm truncate">{file.name}</span>
                  <span className="text-xs text-gray-500">
                    {(file.size / 1024).toFixed(1)} Ko
                  </span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="text-gray-400 hover:text-red-500"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={isUploading}
            className={`w-full py-3 rounded-lg font-medium transition-colors ${
              isUploading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            {isUploading ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-5 h-5 border-t-2 border-white rounded-full animate-spin"></div>
                Envoi en cours...
              </div>
            ) : (
              'Confirmer l\'envoi'
            )}
          </button>
        </div>
      )}
    </div>
  );
}