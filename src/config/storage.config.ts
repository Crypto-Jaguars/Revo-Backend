import multer from 'multer';

export const storageConfig = {
  storage: multer.diskStorage({
    destination: './uploads', // Temporary storage
    filename: (req, file, cb) => {
      cb(null, `${Date.now()}-${file.originalname}`);
    },
  }),
  limits: { fileSize: 1 * 1024 * 1024 * 1024 }, // 1GB max file size
};
