export type Iversion = string
type arg = { name: string; desc: string };

type object_list = {
  id: string;
  signature: string;
  description: string;
  args?: arg[];
};

export type NotificationMethods = Record<
  string,
  {
    signature?: string;
    description?: string|any;
    args?: arg[];
  }
>;

export interface IReferencePage {
  NOTIFICATION_METHODS: NotificationMethods;
  HANDLER_METHODS: object_list[];
  STYLE_ATTRIBUTES?: object_list[];
}