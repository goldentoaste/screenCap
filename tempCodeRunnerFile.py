
        self.exitButton = Button(self.frame3, text="Exit", command=self.main.quit).pack(
            side=RIGHT, anchor="e")
        self.aboutButton = Button(self.frame3, text="About").pack(
            side=RIGHT, anchor="e")

        self.frame3.pack(side=TOP, padx=10, pady=(10, 5), expand=True, fill=X)


if __name__ == "__main__":
    main = MainWindow()