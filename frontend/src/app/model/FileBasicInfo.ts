import {FileTypeEnum} from "./enums/FileTypeEnum";

export interface FileBasicInfo {
  file: string,
  type: FileTypeEnum,
  url: string
}
