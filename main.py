from utils import *



def main():
    sheet = dailysheet("~/Downloads/CDN.xlsx")

    miners = ["72529", "48256", "69455", "72703", "76698", "200001", "300001", "400001", "100001", "69890"]
    for m in miners:
        sheet.save_to_json(m)
    #sheet.compare()





if __name__ == "__main__":
    main()
