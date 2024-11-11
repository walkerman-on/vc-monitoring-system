## Демо

---

## Описание проекта

---

## Запуск проекта

```
npm install - устанавливаем зависимости
npm start - запуск UI
npm run server - запуск сервера
```

---

## Скрипты

- `npm run start` - Запуск frontend проекта на webpack dev server
- `npm run server` - Запуск json-server
- `npm run build:prod` - Сборка в prod режиме
- `npm run build:dev` - Сборка в dev режиме (не минимизирован)
- `npm run eslint` - Проверка ts файлов линтером
- `npm run stylelint` - Проверка scss файлов style линтером
- `npm run prettier` - Исправление ts и scss файлов
- `npm run prettier-check` - Проверка, есть ли доступные к исправлению ts и scss файлы

---

## Архитектура проекта

Проект написан в соответствии с методологией Feature Sliced Design
- [ ] Ссылка на документацию - [Feature Sliced Design](https://feature-sliced.design/docs/get-started/tutorial)

---

## Линтинг

В проекте используется eslint для проверки typescript кода и stylelint для проверки файлов со стилями.

##### Запуск линтеров

- `npm run eslint` - Проверка ts файлов линтером
- `npm run stylelint` - Проверка scss файлов style линтером
- `npm run prettier` - Исправление ts и scss файлов
- `npm run prettier-check` - Проверка, есть ли доступные к исправлению ts и scss файлы

---

## Конфигурация проекта

Для разработки проект содержит Webpack конфиг

Вся конфигурация хранится в ./config

---

## pre commit хуки

В прекоммит хуках проверяем проект линтерами

---

### Работа с данными

Взаимодействие с данными осуществляется с помощью Redux Toolkit.

---

## Технологии
React, React Router, TypeScript, Redux Toolkit, SCSS module, Webpack

---